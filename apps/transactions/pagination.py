"""
Custom pagination classes for the transactions app.
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    """
    Custom pagination class with configurable page size.
    
    Features:
    - Default page size: 20
    - Maximum page size: 100
    - Allows client to specify page size via 'page_size' query parameter
    - Returns enhanced pagination metadata
    
    Query Parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    
    Response Format:
    {
        "count": 100,
        "next": "http://api.example.org/transactions/?page=3",
        "previous": "http://api.example.org/transactions/?page=1",
        "total_pages": 5,
        "current_page": 2,
        "page_size": 20,
        "results": [...]
    }
    """
    
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
    
    def get_paginated_response(self, data):
        """
        Return paginated response with enhanced metadata.
        
        Args:
            data: Serialized data for current page
            
        Returns:
            Response: Paginated response with metadata
        """
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'page_size': self.page.paginator.per_page,
            'results': data
        })
