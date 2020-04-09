import random
import string

import django
from django.contrib.auth.models import User
from django.core.validators import URLValidator
from django.db import models

from shortener import settings


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Url(BaseModel):
    user = models.ForeignKey(
        to=User,
        related_name='url',
        on_delete=models.DO_NOTHING,
        verbose_name='url'
    )
    link = models.TextField(
        validators=[URLValidator()],
        verbose_name='link'
    )
    uri = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='uri'
    )

    @classmethod
    def get_by_uri(cls: 'Url', uri: str) -> 'Url':
        return cls.objects.filter(uri=uri).first()

    @staticmethod
    def create_shorten(count: int) -> str:
        return ''.join(
            random.choice(string.ascii_uppercase + string.digits) for _ in
            range(count))

    @property
    def shorten_url(self: 'Url') -> str:
        return '{}{}'.format(settings.BASE_SYSTEM_URL, self.uri)

    def custom_uri(self: 'Url') -> None:
        if self.uri:
            if self.get_by_uri(self.uri):
                self.uri = '{}{}'.format(self.uri, self.create_shorten(1))
        else:
            self.uri = self.create_shorten(5)

    def save(self, *args, **kwargs):
        if self._state.adding:
            try:
                self.custom_uri()
                return super().save(*args, **kwargs)
            except django.db.utils.IntegrityError as e:
                print(e)
                self.id = None
                self.uri = None

                return self.save(*args, **kwargs)
        return super().save(*args, **kwargs)

    def __str__(self: 'Url') -> str:
        return self.link
