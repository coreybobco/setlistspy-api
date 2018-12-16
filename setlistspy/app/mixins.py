from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework.mixins import ListModelMixin

from django.conf import settings

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)

class SetSpyListModelMixin(ListModelMixin):

    @method_decorator(cache_page(CACHE_TTL))
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer_class = self.get_serializer_class()
        context = self.get_serializer_context()
        if hasattr(serializer_class, "setup_queryset"):
            queryset = serializer_class.setup_queryset(queryset, context)
        page = self.paginate_queryset(queryset)
        serializer = serializer_class(page, many=True, context=context)
        return self.get_paginated_response(serializer.data)