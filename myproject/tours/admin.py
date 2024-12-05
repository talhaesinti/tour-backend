from django.contrib import admin
from django.utils.html import format_html
from .models import DomesticTour, InternationalTour, Region, Banner


class DomesticTourAdmin(admin.ModelAdmin):
    list_display = ('name', 'airline', 'start_date', 'end_date', 'price', 'is_active', 'thumbnail_preview')
    list_filter = ('is_active',)  # Sadece aktiflik durumuna göre filtreleme
    search_fields = ('name', 'airline')  # İsim ve havayoluna göre arama
    ordering = ('-start_date',)  # Başlangıç tarihine göre azalan sıralama

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.thumbnail.url)
        return "-"
    thumbnail_preview.short_description = 'Thumbnail'


class InternationalTourAdmin(admin.ModelAdmin):
    list_display = ('name', 'airline', 'start_date', 'end_date', 'price', 'region', 'is_active', 'thumbnail_preview')
    list_filter = ('is_active', 'region')  # Aktiflik ve bölgeye göre filtreleme
    search_fields = ('name', 'airline', 'region__name')  # İsim, havayolu ve bölgeye göre arama
    ordering = ('-start_date',)  # Başlangıç tarihine göre azalan sıralama

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.thumbnail.url)
        return "-"
    thumbnail_preview.short_description = 'Thumbnail'
    


class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'thumbnail_preview')
    list_filter = ('is_active',)  # Aktifliğe göre filtreleme
    search_fields = ('name',)  # Bölge adına göre arama
    ordering = ('name',)  # Bölge adına göre alfabetik sıralama

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.thumbnail.url)
        return "-"
    thumbnail_preview.short_description = 'Thumbnail'


class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'is_active')  # Thumbnail alanı çıkarıldı, tür ve aktiflik eklendi
    list_filter = ('type', 'is_active')  # Tür ve aktiflik durumuna göre filtreleme
    search_fields = ('title',)  # Başlığa göre arama
    ordering = ('title',)  # Başlığa göre alfabetik sıralama


# Admin'e kayıt işlemleri
admin.site.register(DomesticTour, DomesticTourAdmin)
admin.site.register(InternationalTour, InternationalTourAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Banner, BannerAdmin)
