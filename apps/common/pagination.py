"""Project-wide pagination (single source of truth, referenced in settings)."""
from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    """Page-number pagination that keeps working under arbitrary ordering.

    Page-number (offset) pagination is used deliberately: cursor pagination
    cannot paginate over a dynamically-computed ``distance`` ordering, which
    the Ride List API requires.
    """

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
