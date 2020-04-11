# TSP Project
FROM debian:stretch-slim

MAINTAINER Maza Fard "Mazafard@gmail.com"

# Install System requirnment pakcages
RUN apt-get update && apt-get install -y python3 \
	python3-dev \
	python3-setuptools \
	python3-pip \
	nginx \
	xvfb \
	libmariadbclient-dev \
	curl
#        && pip3 install uwsgi


# Copy requirenments
COPY ["entrypoint.sh", "requirements.txt", "/"]


# Install python packages
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy project files
COPY [".", "/var/www"]

RUN apt-get autoremove --purge -y  gcc && \
        chmod +x /entrypoint.sh && \
        chown -R www-data. /var/www

WORKDIR "/var/www"



ENTRYPOINT ["/entrypoint.sh"]
