#!/bin/bash
if [ $1 == "uwsgi" ]; then
        shift
        cd /var/www && python3 manage.py migrate
        uwsgi --uid www-data --gid www-data --plugins=python3 --chdir=/var/www --socket=0.0.0.0:9000 $@
elif [ $1 == "celery" ]; then
	shift
	/usr/local/bin/celery worker -B -A $@
elif [ $1 == "nginx" ]; then
	cd /var/www && echo "yes" | python3 manage.py collectstatic
	chown -R www-data. /var/www

	cat >/etc/nginx/sites-available/default <<EOL
server {
       listen 80;

       root /var/www;
       client_max_body_size 50M;
       location / {
               include         uwsgi_params;
               proxy_pass      http://$_CGI:9000;
       }

       location /static {
               alias /var/www/static;
       }

       location /cdn {
               alias /var/www/uploads;
       }
}
server {
       listen 8080;

       root /var/www/uploads;
       client_max_body_size 50M;

       location / {
           add_header Access-Control-Allow-Origin "*";
	       alias /var/www/uploads/;
       }

       location /static {
                add_header Access-Control-Allow-Origin "*";
               alias /var/www/static;
       }

}
EOL
	# Nginx conf
        cat >/etc/nginx/nginx.conf <<EOL
user www-data;
worker_processes auto;
pid /run/nginx.pid;
daemon off;

events {
    worker_connections  1024;
}


http {
        sendfile on;
        tcp_nopush on;
        tcp_nodelay on;
        keepalive_timeout 65;
        types_hash_max_size 2048;
        include       /etc/nginx/mime.types;
        default_type  application/octet-stream;

        #tcp_nopush     on;

        ssl_protocols TLSv1 TLSv1.1 TLSv1.2; # Dropping SSLv3, ref: POODLE
        ssl_prefer_server_ciphers on;

        gzip on;
        gzip_http_version  1.1;
        gzip_comp_level    5;
        gzip_min_length    256;
        gzip_proxied       any;
        gzip_vary          on;
        gzip_types
        application/atom+xml
        application/javascript
        application/json
        application/rss+xml
        application/vnd.ms-fontobject
        application/x-font-ttf
        application/x-web-app-manifest+json
        application/xhtml+xml
        application/xml
        font/opentype
        image/svg+xml
        image/x-icon
        text/css
        text/plain
        text/x-component;

        include /etc/nginx/conf.d/*.conf;
        include /etc/nginx/sites-enabled/*;
}
EOL
        nginx
elif [ $1 == "bash" ]; then
	bash
fi
