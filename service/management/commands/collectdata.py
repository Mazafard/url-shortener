import datetime
from django.core.management.base import BaseCommand
from django_redis import get_redis_connection


class Command(BaseCommand):
    help = 'Create new Job Fair'


    def make_key(*arg):
        return ':'.join(arg)

    def handle(self, *args, **options):
        conn = get_redis_connection('redis')
        all = conn.keys('uri:*:session_id:*')
        # all = conn.keys('*')
