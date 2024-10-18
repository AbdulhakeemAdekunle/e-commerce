from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet
from authsys.models import User
from .serializers import RegisterSerializer


# Create your views here.

# RegisterView that support only a POST request using CreateAPIView
class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer