from django.shortcuts import get_object_or_404
from rest_framework import viewsets, pagination, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from django.db.models import (
    Q, 
    Exists, 
    OuterRef, 
    Value, 
    BooleanField,
)


from .models import (
    Blog,
    Category,
    Tag,
    Favourite,
)

from .serializers import (
    BlogSerializer,
    ReviewSerializer,
    BlogDetailSerializer,
    CategorySerializer,
    TagSerializer,
)
# Create your views here.

# Custom pagination class
class PaginationView(pagination.PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 100

# List all Categories
class CategoryListView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer 

# List all Tags
class TagListView(ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer   

   
class BlogViewSet(viewsets.ModelViewSet):
    # ViewSet for CRUD operations on Blogs
    # Optimized for performance
    # Use the `get_queryset` method to filter the queryset based on the user
    # Use the `perform_create` method to set the user before saving the object 
    
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter the queryset based on the user
        # Use select_related and prefetch_related for better performance
        # Use `filter` instead of `all` to avoid fetching all objects
        return Blog.objects.filter(user=self.request.user) \
                           .select_related('category', 'user') \
                           .prefetch_related('tags', 'blog_reviews__user')
    

    def perform_create(self, serializer):
        # Set the user before saving the object
        serializer.save(user=self.request.user)


# List all Blogs with pagination or limit the queryset
# Optimized for performance
class BlogListView(ListAPIView):
    serializer_class = BlogSerializer
    pagination_class = PaginationView  # Default pagination class

    def get_queryset(self):
        # Get the `latest` parameter from the request
        latest = self.request.query_params.get('latest', None)
        user = self.request.user # Get the user from the request

        
        # Annotate `is_favourited` only if the user is authenticated
        # Use `Exists` and `OuterRef` for better performance
        if user.is_authenticated:
            queryset = Blog.objects.annotate(
                is_favourited=Exists(Favourite.objects.filter(user=user, blog=OuterRef('pk')))
            )
        else:
            queryset = Blog.objects.annotate(
                is_favourited=Value(False, output_field=BooleanField())
            )

        queryset = queryset.select_related('category', 'user') \
                       .prefetch_related('tags', 'blog_reviews__user') \
                       .order_by('-created_date')

        # If the `latest` parameter is provided, limit the queryset
        if latest is not None and latest.isdigit():
            # If 'latest' is provided, we don't need pagination
            self.pagination_class = None
            queryset = queryset[:int(latest)]

        return queryset
    

# Retrieve a single Blog with reviews
# Optimized for performance
class BlogDetailView(RetrieveAPIView):
    queryset = Blog.objects.select_related('category', 'user') \
                            .prefetch_related('tags', 'blog_reviews__user')
    serializer_class = BlogDetailSerializer
    lookup_field = 'slug'  # You can still use slug for easy URL access
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Annotate `is_favourited` for the single blog
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_favourited=Exists(Favourite.objects.filter(user=user, blog=OuterRef('pk')))
            )
        else:
            queryset = queryset.annotate(
                is_favourited=Value(False, output_field=BooleanField())
            )
        return queryset
    
    # Override the `get_serializer_class` method to use different serializers
    # Use the ReviewSerializer for POST requests
    # Use the BlogDetailSerializer for GET requests
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReviewSerializer
        return BlogDetailSerializer
    
    # Override the `get_object` method to prefetch related objects
    # This method is called before the view retrieves the object
    def perform_create(self, serializer):
        blog = self.get_object()
        serializer.save(user=self.request.user, blog=blog)
    
    # Override the `post` method to handle review creation
    # This method is called when a POST request is made to the view
    # Use the `perform_create` method to save the review
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# For add and delete favourite
# Optimized for performance
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
        # Use `delete()` directly with a filter for better efficiency
        deleted, _ = Favourite.objects.filter(user=user, blog=blog).delete()

        if deleted:
            return Response({"message": "Blog removed from favorites"}, status=status.HTTP_200_OK)
        return Response({"message": "Blog not found in favorites"}, status=status.HTTP_404_NOT_FOUND)


# for get all favourite blogs
# Optimized for performance
class BlogFavouriteListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        favourites = Blog.objects.filter(favourited_by__user=user) \
                                   .select_related('category', 'user') \
                                   .prefetch_related('tags', 'blog_reviews__user')
        serializer = BlogSerializer(favourites, many=True, context={'request': request})
        return Response(serializer.data)
    

# Filter Blogs by category
# Optimized for performance
class BlogCategoryFilterView(ListAPIView):
    serializer_class = BlogSerializer

    def get_queryset(self):
        # Get the category ID from query params
        category_id = self.request.query_params.get('category', None)
        
        # If no category_id is provided, return an empty queryset
        if category_id is None:
            return Blog.objects.none()

        # Filter the Blogs by category ID
        queryset = Blog.objects.select_related('category', 'user') \
                                 .prefetch_related(
                                     'tags', 'blog_reviews__user'  # Prefetch tags, reviews and the users who created them
                                 ) \
                                 .filter(category__id=category_id) \
                                 .order_by('-created_date')
        
        return queryset


# Filter Blogs by tags
# Optimized for performance
class BlogTagFilterView(ListAPIView):
    serializer_class = BlogSerializer

    def get_queryset(self):
        # Get the tags from query parameters
        tags = self.request.query_params.get('tags', None)
        
        # If no tags are provided, return an empty queryset
        if not tags:
            return Blog.objects.none()

        # Split the comma-separated tags into a list and strip any extra whitespace
        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]

        # Filter blogs that are associated with the provided tags
        queryset = Blog.objects.select_related('category', 'user') \
                               .prefetch_related(
                                   'tags', 'blog_reviews__user'  # Prefetch tags, reviews, and the users who created them
                               ) \
                               .filter(tags__title__in=tag_list) \
                               .distinct() \
                               .order_by('-created_date')
        
        return queryset
    

# Search Blogs by title or tags
# Optimized for performance
class BlogSearchView(ListAPIView):
    
    serializer_class = BlogSerializer
    filter_backends = [SearchFilter]


    def get_queryset(self):
        queryset = Blog.objects.select_related('category', 'user') \
                                .prefetch_related('tags', 'blog_reviews__user')
        
        search_query = self.request.query_params.get('find', None)
        if search_query:
            # Use Q objects to search across related fields
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(category__title__icontains=search_query) | # category is a foreign key
                Q(tags__title__icontains=search_query) # tags is a many-to-many field
            ).distinct()  # Use distinct to avoid duplicates due to join operations
        
        return queryset

    