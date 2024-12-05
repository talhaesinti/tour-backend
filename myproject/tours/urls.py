from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import DomesticTourViewSet, InternationalTourViewSet, RegionViewSet, BannerViewSet, RegisterView

router = DefaultRouter()
router.register(r'domestic-tours', DomesticTourViewSet, basename='domestic-tours')
router.register(r'international-tours', InternationalTourViewSet, basename='international-tours')
router.register(r'regions', RegionViewSet, basename='regions')  # Burada basename parametresi ekleniyor
router.register(r'banners', BannerViewSet, basename='banners')

urlpatterns = [
    path('', include(router.urls)),  # Mevcut API yönlendirmeleri
    path('register/', RegisterView.as_view(), name='register'),  # Kullanıcı kaydı için
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Token almak için
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Token yenilemek için
]
