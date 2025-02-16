from rest_framework import generics, permissions
from .serializers import RegisterSerializer, UserProfileSerializer
from .models import User
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class ProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

# For Login, we use SimpleJWT's TokenObtainPairView.
