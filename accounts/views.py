from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse


# Register
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

# Login
class MyTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]

# Token Refresh
class MyTokenRefreshView(TokenRefreshView):
    permission_classes = [AllowAny]

# Logout
@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "refresh": {"type": "string", "example": "your_refresh_token_here"},
            },
            "required": ["refresh"]
        }
    },
    responses={
        205: OpenApiResponse(description="Token blacklisted successfully."),
        400: OpenApiResponse(description="Invalid or missing token."),
    },
    description="logout user and block refresh token"
)
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Expects body containing refresh token:
        {
            "refresh": "<refresh_token>"
        }
        """
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
