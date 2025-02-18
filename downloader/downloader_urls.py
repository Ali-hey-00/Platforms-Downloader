from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    UserRegistrationView,
    UserProfileView,
    MediaDownloadView,
    DownloadHistoryViewSet,
)

router = DefaultRouter()
router.register(r'history', DownloadHistoryViewSet, basename='history')

urlpatterns = [
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('download/', MediaDownloadView.as_view(), name='download'),
] + router.urls