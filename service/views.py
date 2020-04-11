from celery import shared_task
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render, redirect

# Create your views here.
from django.utils.datetime_safe import datetime
from django.views import generic
from django.views.generic import TemplateView
from django.views.generic.list import MultipleObjectMixin
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from service import serializers, errors
from service.models import Url
from service.response import ErrorResponse
from user_agents import parse


# def index(request):
#     """View function for home page of site."""
#     # Generate counts of some of the main objects
#     # num_url = Url.objects.all().count()
#     # # num_instances = BookInstance.objects.all().count()
#     # # Available copies of books
#     # # num_instances_available = BookInstance.objects.filter(status__exact='a').count()
#     # # num_authors = Author.objects.count()  # The 'all()' is implied by default.
#     #
#     # # Number of visits to this view, as counted in the session variable.
#     # num_visits = request.session.get('num_visits', 0)
#     # request.session['num_visits'] = num_visits + 1
#     #
#     # # Render the HTML template index.html with the data in the context variable.
#     # return render(
#     #     request,
#     #     'index.html',
#     #     context={'num_books': num_url,
#     #              'num_visits': num_visits},
#     )

class HomePage(TemplateView):
    template_name = 'index.html'


class BaseListView(generic.ListView):
    """A base view for displaying a single object."""

    def get_queryset(self):
        if self.request.user.is_staff:
            return super().get_queryset()
        return super().get_queryset().filter(
            user=self.request.user
        )


class BaseDetailView(generic.DetailView):
    """A base view for displaying a single object."""

    def get(self, request, *args, **kwargs):
        if self.request.user.is_staff:
            return super().get(request, *args, **kwargs)

        self.object = self.get_object(super().get_queryset().filter(
            user=self.request.user
        ))
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class UrlListView(LoginRequiredMixin, BaseListView):
    """Generic class-based view for a list of urls."""
    model = Url
    paginate_by = 10


class UrlDetailView(LoginRequiredMixin, generic.DetailView):
    """Generic class-based detail view for a url."""
    model = Url


class BaseApiView(APIView):
    pass


class ShorterApiView(BaseApiView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = serializers.UrlSerializer(data=request.data)

        if not serializer.is_valid():
            return ErrorResponse(
                errors.CLIENT_REQUEST_IS_NOT_VALID,
                errors=serializer.errors
            )

        serializer.save()

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


def make_key(*arg):
    return ':'.join(arg)


@shared_task
def set_redis_stat(session_id, request, uri, time):
    conn = get_redis_connection('redis')
    pipe = conn.pipeline(True)
    pipe.hincrby(uri, 'view', 1)
    user_agent = parse(request.META['HTTP_USER_AGENT'])
    key_uri_session_id = make_key('uri', uri, 'session_id', session_id)
    key_uri_session_id_date = make_key(key_uri_session_id, 'date')
    data = {
        'browser': ("%s %s" % (user_agent.browser.family, user_agent.browser.version_string)).strip(),
        'device': user_agent.is_pc and "PC" or user_agent.device.family,
        'os': ("%s %s" % (user_agent.os.family, user_agent.os.version_string)).strip(),
    }
    pipe.hmset(key_uri_session_id, data)

    pipe.lpush(key_uri_session_id_date, time)
    pipe.execute()


def get_uri(connection, uri):
    if not connection.hmget(uri, 'link'):
        raise Http404()
    return str(connection.hmget(uri, 'link')[0], 'utf-8')


class RedirectView(TemplateView):

    def get(self, request, uri):
        con = get_redis_connection('redis')

        try:
            link = get_uri(con, uri)
            session_id = request.session._get_or_create_session_key()
            set_redis_stat(session_id, request, uri, datetime.now().timestamp())
            return redirect(to=link)

        except:
            raise Http404()


class AnalyticsView(BaseApiView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = serializers.AnalyticsSerializer(data=request.data)

        if not serializer.is_valid():
            return ErrorResponse(
                errors.CLIENT_REQUEST_IS_NOT_VALID,
                errors=serializer.errors
            )
        return Response(data=serializer.data, status=status.HTTP_200_OK)
