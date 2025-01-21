from django.shortcuts import get_object_or_404
from rest_framework import viewsets, pagination, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django.db.models import Q

from .models import (
    Blog,
    Favourite,
)

from .serializers import (
    BlogSerializer,
    ReviewSerializer,
)
# Create your views here.

# Custom pagination class
class PaginationView(pagination.PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    
class BlogViewSet(viewsets.ModelViewSet):
    """
    A viewset for creating, updating, and managing blogs by the logged-in user.
    """
    serializer_class = BlogSerializer  # Replace with the appropriate serializer for your Blog model
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Returns blogs authored by the logged-in user.
        """
        return Blog.objects.filter(user=self.request.user) \
                           .select_related('category', 'user') \
                           .prefetch_related('tags')

    def perform_create(self, serializer):
        """
        Automatically sets the logged-in user as the author when creating a blog
        and generates a unique slug.
        """
        serializer.save(user=self.request.user)


# List all Blogs with pagination or limit the queryset
class BlogListView(ListAPIView):
    serializer_class = BlogSerializer
    pagination_class = PaginationView  # Default pagination class

    def get_queryset(self):
        # Get the `latest` parameter from the request
        latest = self.request.query_params.get('latest', None)

        # Base queryset
        queryset = Blog.objects.select_related('category').prefetch_related('tags').order_by('-created_date')

        # If the `latest` parameter is provided, limit the queryset
        if latest is not None and latest.isdigit():
            queryset = queryset[:int(latest)]
            # If 'latest' is provided, we don't need pagination
            self.pagination_class = None

        return queryset
    

class BlogDetailView(RetrieveAPIView):
    queryset = Blog.objects.select_related('category', 'user') \
                            .prefetch_related('blog_reviews')
    serializer_class = BlogSerializer
    lookup_field = 'slug'  # You can still use slug for easy URL access
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReviewSerializer
        return BlogSerializer

    def perform_create(self, serializer):
        blog = self.get_object()
        serializer.save(user=self.request.user, blog=blog)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# For add and delete favourite
class BlogFavouriteView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, id):
        """
        Add a blog to the user's favorites.
        """
        user = request.user
        blog = get_object_or_404(Blog, id=id)
        favourite, created = Favourite.objects.get_or_create(user=user, blog=blog)

        if created:
            return Response({"message": "Blog added to favorites"}, status=status.HTTP_201_CREATED)
        return Response({"message": "Blog is already in favorites"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        """
        Remove a Blog from the user's favorites.
        """
        user = request.user
        blog = get_object_or_404(Blog, id=id)
        favourite = Favourite.objects.filter(user=user, blog=blog).first()

        if favourite:
            favourite.delete()
            return Response({"message": "Blog removed from favorites"}, status=status.HTTP_200_OK)
        return Response({"message": "Blog not found in favorites"}, status=status.HTTP_404_NOT_FOUND)

# for get all favourite blogs
class BlogFavouriteListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        favourites = Blog.objects.filter(favourited_by__user=user) \
                                   .select_related('category', 'user') \
                                   .prefetch_related('tags')
        serializer = BlogSerializer(favourites, many=True, context={'request': request})
        return Response(serializer.data)
    

class BlogCategoryFilterView(ListAPIView):
    serializer_class = BlogSerializer

    def get_queryset(self):
        # Get the category ID from query params
        category_id = self.request.query_params.get('category', None)
        
        # If no category_id is provided, return an empty queryset
        if category_id is None:
            return Blog.objects.none()

        # Filter the Blogs by category ID
        queryset = Blog.objects.select_related('category') \
                                 .prefetch_related(
                                     'tags'  # Prefetch reviews and the users who created them
                                 ) \
                                 .filter(category__id=category_id) \
                                 .order_by('-created_at')
        
        return queryset
    

class BlogSearchView(ListAPIView):
    
    serializer_class = BlogSerializer
    filter_backends = [SearchFilter]


    def get_queryset(self):
        queryset = Blog.objects.select_related('category').prefetch_related('tags')
        
        search_query = self.request.query_params.get('search', None)
        if search_query:
            # Use Q objects to search across related fields
            queryset = queryset.filter(
                Q(title__icontains=search_query)
            ).distinct()  # Use distinct to avoid duplicates due to join operations
        
        return queryset

    