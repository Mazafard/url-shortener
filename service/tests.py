from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from model_bakery import baker

from service.models import Url

class UrlModelTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods

        cls.user = baker.make(User)
        Url.objects.create(link='google.com', uri='', user=cls.user)


    def test_url_label(self):
        url = Url.objects.get(id=1)
        field_label = url._meta.get_field('link').verbose_name
        self.assertEquals(field_label, 'link')

