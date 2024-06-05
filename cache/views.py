import logging
from django.http import JsonResponse
from django.core.cache import cache


logger = logging.getLogger(__name__)


def index(request):
    key = request.GET.get('key', None)
    if key is not None:
        value = cache.get(key)
        if not value:
            cache.set(key, key)
        elif key != value:
            message = f"*** Keys mismatch detected - key: {key}, value: {value} ***"
            logger.warning(message)
            return JsonResponse({ "error": message }, status=409)
        return JsonResponse({ "result": value })
    else:
        return JsonResponse({ "error": "No key provided in query parameters." }, status=400)
    