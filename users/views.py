from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .models import User
# Create your views here.
from .serializers import (
    RegisterSerializer,
    UserProfileSerializer,
)

class RegistrationView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": "success", "message": "User Registration Successfully"}, 
                status = status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
    

class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        user = authenticate(request, email = email, password = password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "status": "success",
                    "username": user.username,
                    "token": str(refresh.access_token),
                },
                status = status.HTTP_200_OK,
            )
            
        return Response(
            {"status": "unauthorized", "message": "Invalid email or password"},
            status = status.HTTP_401_UNAUTHORIZED,   
        )


class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def perform_update(self, serializer):
        serializer.save()  # No need to pass user here since the serializer handles it