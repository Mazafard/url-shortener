from rest_framework import serializers

from service.models import Url


class BaseModelSerializer(serializers.ModelSerializer):
    pass


class UrlSerializer(BaseModelSerializer):
    uri = serializers.CharField(
        required=False,
        allow_null=True,
        allow_blank=True,
        min_length=4
    )
    link = serializers.CharField(read_only=True)

    def validate_uri(self, value):
        if Url.get_by_uri(value):
            raise serializers.ValidationError('Duplicated uri')
        return value

    class Meta:
        model = Url
        exclude = ('created_at', 'updated_at', 'id')

#
# class AnalyticsSerializer(BaseModelSerializer):
#     uri = serializers.CharField(
#         required=False,
#         allow_null=True,
#         allow_blank=True,
#         min_length=4
#     )
#     link = serializers.CharField(read_only=True)
#
#     def validate_uri(self, value):
#         if Url.get_by_uri(value):
#             raise serializers.ValidationError('Duplicated uri')
#         return value
#
#     class Meta:
#         model = Url
#         exclude = ('created_at', 'updated_at', 'id')
