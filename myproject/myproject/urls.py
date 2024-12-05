from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger için şema yapılandırması
schema_view = get_schema_view(
    openapi.Info(
        title="Tour API",
        default_version='v1',
        description="Tour API documentation with Swagger",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,  # Public olarak ayarlandı
    permission_classes=(permissions.AllowAny,),  # Swagger dokümantasyonu herkes tarafından erişilebilir
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('tours.urls')),  # Turlar için oluşturduğumuz API'yi ekliyoruz
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # Swagger UI
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),  # Redoc UI
]

# Medya dosyalarının geliştirme ortamında düzgün şekilde gösterilmesini sağlıyoruz
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
