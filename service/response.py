from rest_framework.response import Response as BaseResponse


class Response(BaseResponse):
    pass


class ErrorResponse(Response):
    def __init__(self, error_summery, errors=None, extra_data=None, *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        if errors is None:
            errors = []

        self.data = {
            'errors': errors,
            'code': error_summery['code'],
            'message': error_summery['message'],
            'data': extra_data
        }

        self.status_code = error_summery['status_code']
