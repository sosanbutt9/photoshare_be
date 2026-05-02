from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        detail = response.data
        if isinstance(detail, dict) and len(detail) == 1 and "detail" in detail:
            payload = {"success": False, "detail": detail["detail"]}
        else:
            payload = {"success": False, "errors": detail}
        response.data = payload
    return response
