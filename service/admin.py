from django.contrib import admin

# Register your models here.

from service.models import Url


@admin.register(Url)
class UrlAdmin(admin.ModelAdmin):
    list_display = (
        'link',
        'uri',
        'created_at',
        'updated_at',
    )
    exclude = ('user',)

    date_hierarchy = 'created_at'

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)
