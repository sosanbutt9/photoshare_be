from rest_framework.filters import SearchFilter


class QueryParamSearchFilter(SearchFilter):
    """Use `q` as the query parameter for search (frontend-friendly)."""

    search_param = "q"
