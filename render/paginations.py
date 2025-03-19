from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PaginationProjects(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    # max_page_size = 100


class ProjectTaskPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data, total_count, next_link, previous_link):
        return Response({
            'count': total_count,
            'next': next_link,
            'previous': previous_link,
            'results': data
        })
