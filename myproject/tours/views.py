from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User
from .models import DomesticTour, InternationalTour, Region, Banner
from .serializers import (
    DomesticTourSerializer,
    InternationalTourSerializer,
    RegionSerializer,
    BannerSerializer,
    RegisterSerializer,
)
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


# Kullanıcı kaydı için APIView
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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = DomesticTour.objects.all()
        is_active = self.request.query_params.get('is_active', 'all')
        if is_active.lower() == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active.lower() == 'false':
            queryset = queryset.filter(is_active=False)
        return queryset


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
        """
        Query parametreleriyle yurt dışı turlarını filtreler.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = InternationalTour.objects.all()
        region_id = self.request.query_params.get('region_id', None)
        region_slug = self.request.query_params.get('region_slug', None)
        is_active = self.request.query_params.get('is_active', 'all')

        # Region ID ile filtreleme
        if region_id:
            queryset = queryset.filter(region_id=region_id)

        # Region Slug ile filtreleme
        if region_slug:
            queryset = queryset.filter(region__slug=region_slug)

        # is_active durumuna göre filtreleme
        if is_active.lower() == 'true':
            queryset = queryset.filter(is_active=True)
        elif is_active.lower() == 'false':
            queryset = queryset.filter(is_active=False)

        return queryset



class RegionViewSet(viewsets.ModelViewSet):
    serializer_class = RegionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)

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
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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
