
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegistrationView,
    LoginView,
    UserProfileViewSet,
)

router = DefaultRouter()
router.register(r'profile', UserProfileViewSet, basename='user-profile')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegistrationView.as_view(), name = 'register'),
    path('login/', LoginView.as_view(), name = 'login'),
]