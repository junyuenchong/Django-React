from django.http import HttpRequest, HttpResponseNotModified
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.http import http_date, parse_http_date_safe

from apps.items.models import Item
from apps.items.helpers.list_cache import make_items_list_cache_key


def build_items_etag(request: HttpRequest) -> str:
    """Build a weak ETag value from the current list cache key."""
    return f'W/"{make_items_list_cache_key(request.query_params)}"'


def build_items_last_modified(queryset: QuerySet[Item]) -> str | None:
    """Return RFC1123 date of latest item update for Last-Modified header."""
    latest = queryset.only("updated_at").order_by("-updated_at").first()
    if latest is None:
        return None
    return http_date(latest.updated_at.timestamp())


def should_return_not_modified(
    request: HttpRequest,
    queryset: QuerySet[Item],
    etag_value: str,
    last_modified_value: str | None,
) -> HttpResponseNotModified | None:
    """Check conditional headers and return 304 response when data is unchanged."""
    inm = request.META.get("HTTP_IF_NONE_MATCH")
    if inm and inm == etag_value:
        return _not_modified_response(etag_value, last_modified_value)

    ims = request.META.get("HTTP_IF_MODIFIED_SINCE")
    if not ims or not last_modified_value:
        return None

    ims_ts = parse_http_date_safe(ims)
    latest = queryset.only("updated_at").order_by("-updated_at").first()
    if ims_ts is None or latest is None:
        return None

    latest_ts = int(latest.updated_at.astimezone(timezone.utc).timestamp())
    if latest_ts <= ims_ts:
        return _not_modified_response(etag_value, last_modified_value)
    return None


def add_cache_headers(response, etag_value: str, last_modified_value: str | None):
    """Attach ETag/Last-Modified headers to a normal response."""
    response["ETag"] = etag_value
    if last_modified_value:
        response["Last-Modified"] = last_modified_value
    return response


def _not_modified_response(
    etag_value: str, last_modified_value: str | None
) -> HttpResponseNotModified:
    """Build a 304 response with cache headers."""
    response = HttpResponseNotModified()
    response["ETag"] = etag_value
    if last_modified_value:
        response["Last-Modified"] = last_modified_value
    return response

