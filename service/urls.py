from django.urls import path

from service import views

urlpatterns = [
    path('', views.UrlListView.as_view(), name='urls'),
    path('<int:pk>', views.UrlDetailView.as_view(), name='url-detail'),
]
