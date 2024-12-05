from rest_framework import serializers
from .models import DomesticTour, InternationalTour, Region, Banner, RegionBanner
from django.contrib.auth.models import User

class RegionBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegionBanner
        fields = ['id', 'image', 'title', 'description', 'is_active', 'region']

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['id', 'name', 'slug', 'is_active', 'thumbnail']

class DomesticTourSerializer(serializers.ModelSerializer):
    thumbnail = serializers.ImageField(use_url=True, required=True)
    tour_program_pdf = serializers.FileField(use_url=True, required=False)

    class Meta:
        model = DomesticTour
        fields = [
            'id', 'name', 'airline', 'start_date', 'end_date', 'price',
            'tour_info', 'is_active', 'thumbnail', 'tour_program_pdf',
            'created_at', 'updated_at'
        ]

class InternationalTourSerializer(serializers.ModelSerializer):
    region = RegionSerializer(read_only=True)
    region_id = serializers.PrimaryKeyRelatedField(
        queryset=Region.objects.all(),
        source='region',
        write_only=True
    )

    class Meta:
        model = InternationalTour
        fields = [
            'id', 'name', 'airline', 'start_date', 'end_date', 'price',
            'tour_info', 'is_active', 'region', 'region_id',
            'thumbnail', 'tour_program_pdf', 'created_at', 'updated_at'
        ]

    def validate(self, data):
        region = data.get('region') or self.instance.region
        if region and not region.is_active:
            raise serializers.ValidationError("Seçtiğiniz bölge aktif değil.")
        return data


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
