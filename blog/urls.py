from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BlogViewSet,
    BlogListView,
    BlogDetailView,
    BlogSearchView,
    BlogCategoryFilterView,
    BlogFavouriteView,
    BlogFavouriteListView,
)

router = DefaultRouter()
router.register(r'blogs', BlogViewSet, basename='blog')

urlpatterns = [
    path('blog-detail/<str:slug>/', BlogDetailView.as_view(), name='blog-detail'),
    path('favourites/<int:id>/', BlogFavouriteView.as_view(), name='favourites'),
    path('favourites/', BlogFavouriteListView.as_view(), name='favourites-list'),
    path('all-blogs/', BlogListView.as_view(), name='all-blogs'),
    path('search/', BlogSearchView.as_view(), name='search'),
    path('filter/', BlogCategoryFilterView.as_view(), name='category'),

    path('', include(router.urls)),
]