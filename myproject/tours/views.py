from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.http import JsonResponse, Http404
from django.db.models import Q
from .models import DomesticTour, InternationalTour, Region, Banner, DomesticTourImage, InternationalTourImage
from .serializers import (
    DomesticTourSerializer,
    InternationalTourSerializer,
    RegionSerializer,
    BannerSerializer,
    RegisterSerializer,
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Hata mesajlarını JSON formatında dönen bir fonksiyon
def error_response(message, status_code=status.HTTP_400_BAD_REQUEST):
    return JsonResponse({"error": message}, status=status_code)

class RegisterView(APIView):
    @swagger_auto_schema(
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response("User created successfully"),
            400: "Bad request - validation error",
        },
        operation_description="Bu API, kullanıcı kaydı yapar. Kullanıcı bilgilerini (isim, email vb.) alır ve kayıt işlemi gerçekleştirir.",
    )
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        return error_response(serializer.errors)

domestic_tour_images_param = openapi.Parameter(
    name='new_images',
    in_=openapi.IN_FORM,
    type=openapi.TYPE_FILE,
    description="Birden fazla resim yüklemek için aynı parametrede birden çok dosya seçebilirsiniz.",
    required=False
)

class DomesticTourViewSet(viewsets.ModelViewSet):
    serializer_class = DomesticTourSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_description="Bu API, yurt içi turları listeler. Query parametresi olarak 'is_active' kabul eder ('true', 'false', 'all').",
        manual_parameters=[
            openapi.Parameter(
                'is_active',
                openapi.IN_QUERY,
                description="Aktif veya pasif turları listelemek için ('true', 'false', 'all')",
                type=openapi.TYPE_STRING,
                required=False,
            )
        ],
        responses={200: DomesticTourSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        valid_params = ['is_active']
        for param in request.query_params.keys():
            if param not in valid_params:
                return error_response(f"Geçersiz parametre: {param}")

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Yeni bir yurt içi tur oluşturur.",
        request_body=DomesticTourSerializer,
        consumes=["multipart/form-data"],
        manual_parameters=[domestic_tour_images_param],
        responses={201: DomesticTourSerializer}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tour = serializer.save()

        images = request.FILES.getlist('new_images')
        for img in images:
            DomesticTourImage.objects.create(tour=tour, image=img)

        return Response(self.get_serializer(tour).data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Belirli bir yurt içi tur detayını getirir (id veya slug ile sorgu yapılabilir).",
        manual_parameters=[
            openapi.Parameter(
                'pk',
                openapi.IN_PATH,
                description="Tur ID'si veya Slug değeri",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={200: DomesticTourSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_object(self):
        queryset = self.get_queryset()
        lookup_value = self.kwargs.get(self.lookup_field)

        if lookup_value.isdigit():
            obj = queryset.filter(id=lookup_value).first()
        else:
            obj = queryset.filter(slug=lookup_value).first()

        if not obj:
            raise Http404(f"Tur bulunamadı: {lookup_value}")
        return obj

    def get_queryset(self):
        queryset = DomesticTour.objects.all()
        is_active = self.request.query_params.get('is_active', 'all')
        if is_active.lower() == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active.lower() == 'false':
            queryset = queryset.filter(is_active=False)
        return queryset

international_tour_images_param = openapi.Parameter(
    name='new_images',
    in_=openapi.IN_FORM,
    type=openapi.TYPE_FILE,
    description="Birden fazla resim yüklemek için aynı parametrede birden çok dosya seçebilirsiniz.",
    required=False
)

class InternationalTourViewSet(viewsets.ModelViewSet):
    serializer_class = InternationalTourSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_description=(
            "Bu API, yurt dışı turları listeler. Query parametreleri olarak 'region_id', 'region_slug', "
            "veya 'is_active' kabul eder."
        ),
        manual_parameters=[
            openapi.Parameter(
                'region_id',
                openapi.IN_QUERY,
                description="Region ID'ye göre filtreleme",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                'region_slug',
                openapi.IN_QUERY,
                description="Region slug'a göre filtreleme",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                'is_active',
                openapi.IN_QUERY,
                description="Aktif veya pasif turları listelemek için ('true', 'false', 'all')",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        responses={200: InternationalTourSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        valid_params = ['region_id', 'region_slug', 'is_active']
        for param in request.query_params.keys():
            if param not in valid_params:
                return error_response(f"Geçersiz parametre: {param}")

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = InternationalTour.objects.all()
        region_id = self.request.query_params.get('region_id', None)
        region_slug = self.request.query_params.get('region_slug', None)
        is_active = self.request.query_params.get('is_active', 'all')

        if region_id:
            queryset = queryset.filter(region_id=region_id)

        if region_slug:
            region = Region.objects.filter(slug=region_slug).first()
            if not region:
                return error_response("Geçersiz region_slug.", status_code=status.HTTP_404_NOT_FOUND)
            queryset = queryset.filter(region=region)

        if is_active.lower() == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active.lower() == 'false':
            queryset = queryset.filter(is_active=False)

        return queryset

    def get_object(self):
        queryset = self.get_queryset()
        lookup_value = self.kwargs.get(self.lookup_field)

        if lookup_value.isdigit():
            obj = queryset.filter(id=lookup_value).first()
        else:
            obj = queryset.filter(slug=lookup_value).first()

        if not obj:
            raise Http404(f"Tur bulunamadı: {lookup_value}")
        return obj

class RegionViewSet(viewsets.ModelViewSet):
    serializer_class = RegionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="Bu API, bölgeleri listeler. Query parametresi olarak 'is_active' kabul eder ('true', 'false', 'all').",
        manual_parameters=[
            openapi.Parameter(
                'is_active',
                openapi.IN_QUERY,
                description="Aktif veya pasif bölgeleri listelemek için ('true', 'false', 'all')",
                type=openapi.TYPE_STRING,
                required=False,
            )
        ],
        responses={200: RegionSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        valid_params = ['is_active']
        for param in request.query_params.keys():
            if param not in valid_params:
                return error_response(f"Geçersiz parametre: {param}")

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_object(self):
        queryset = self.get_queryset()
        lookup_value = self.kwargs.get(self.lookup_field)

        if lookup_value.isdigit():
            obj = queryset.filter(id=lookup_value).first()
        else:
            obj = queryset.filter(slug=lookup_value).first()

        if not obj:
            raise Http404(f"Bolge bulunamadı: {lookup_value}")
        return obj

    def get_queryset(self):
        queryset = Region.objects.all()
        is_active = self.request.query_params.get('is_active', 'all')
        if is_active.lower() == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active.lower() == 'false':
            queryset = queryset.filter(is_active=False)
        return queryset

class BannerViewSet(viewsets.ModelViewSet):
    serializer_class = BannerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="Bu API, banner'ları listeler. Query parametreleri olarak 'type' ve 'is_active' kabul eder.",
        manual_parameters=[
            openapi.Parameter(
                'type',
                openapi.IN_QUERY,
                description="Banner türüne göre filtreleme ('home', 'domestic', 'international')",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                'is_active',
                openapi.IN_QUERY,
                description="Aktif veya pasif bannerları listelemek için ('true', 'false', 'all')",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        responses={200: BannerSerializer(many=True)},
    )
    def list(self, request, *args, **kwargs):
        valid_params = ['type', 'is_active']
        for param in request.query_params.keys():
            if param not in valid_params:
                return error_response(f"Geçersiz parametre: {param}")

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = Banner.objects.all()
        banner_type = self.request.query_params.get('type', None)
        is_active = self.request.query_params.get('is_active', 'all')

        if banner_type:
            queryset = queryset.filter(type=banner_type)

        if is_active.lower() == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active.lower() == 'false':
            queryset = queryset.filter(is_active=False)

        return queryset
