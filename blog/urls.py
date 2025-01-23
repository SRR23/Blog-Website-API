from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BlogViewSet,
    BlogListView,
    BlogDetailView,
    BlogSearchView,
    BlogCategoryFilterView,
    BlogTagFilterView,
    BlogFavouriteView,
    BlogFavouriteListView,
    CategoryListView,
    TagListView,
)

router = DefaultRouter()
router.register(r'blogs', BlogViewSet, basename='blog')

urlpatterns = [
    path('blog-detail/<str:slug>/', BlogDetailView.as_view(), name='blog-detail'),
    path('favourites/<int:id>/', BlogFavouriteView.as_view(), name='favourites'),
    path('favourites/', BlogFavouriteListView.as_view(), name='favourites-list'),
    path('all-blogs/', BlogListView.as_view(), name='all-blogs'),
    path('search/', BlogSearchView.as_view(), name='search'),
    path('filter-category/', BlogCategoryFilterView.as_view(), name='category'),
    path('filter-tags/', BlogTagFilterView.as_view(), name='tags'),
    path('categories/', CategoryListView.as_view(), name='categories'),
    path('tags/', TagListView.as_view(), name='tags'),

    path('', include(router.urls)),
]