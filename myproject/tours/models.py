from django.db import models
from django.utils.text import slugify
from django.db.models.signals import post_delete
from django.dispatch import receiver


class RegionBanner(models.Model):
    region = models.ForeignKey('Region', on_delete=models.CASCADE, related_name='region_banners')
    image = models.ImageField(upload_to='region_banners/')
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Banner for {self.region.name}"


class Region(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Region kaydedilirken, aktiflik değişimi varsa bağlı InternationalTour'ları günceller.
        """
        if self.pk:
            old_instance = Region.objects.filter(pk=self.pk).first()
            if old_instance and old_instance.is_active != self.is_active:
                # Bağlı turların durumunu güncelle
                InternationalTour.objects.filter(region=self).update(is_active=self.is_active)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Region silinirken bağlı turları pasif yapar.
        """
        InternationalTour.objects.filter(region=self).update(is_active=False)
        super().delete(*args, **kwargs)



class DomesticTour(models.Model):
    name = models.CharField(max_length=255)
    airline = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tour_info = models.TextField()
    tour_program_pdf = models.FileField(upload_to='tour_programs/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    thumbnail = models.ImageField(upload_to='thumbnails/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class InternationalTour(models.Model):
    name = models.CharField(max_length=255)
    airline = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tour_info = models.TextField()
    tour_program_pdf = models.FileField(upload_to='tour_programs/', blank=True, null=True)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    thumbnail = models.ImageField(upload_to='thumbnails/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """
        Kaydedilirken bölge aktif değilse tur pasif yapılır.
        """
        if not self.region.is_active:
            self.is_active = False
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class TourMedia(models.Model):
    domestic_tour = models.ForeignKey(
        DomesticTour,
        on_delete=models.CASCADE,
        related_name='media',
        blank=True,
        null=True
    )
    international_tour = models.ForeignKey(
        InternationalTour,
        on_delete=models.CASCADE,
        related_name='media',
        blank=True,
        null=True
    )
    media_file = models.FileField(upload_to='tour_media/')
    media_type = models.CharField(
        max_length=20,
        choices=(
            ('image', 'Image'),
            ('video', 'Video'),
        ),
        default='image'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.domestic_tour:
            return f"Media for {self.domestic_tour.name}"
        elif self.international_tour:
            return f"Media for {self.international_tour.name}"
        return "Unassigned Media"


class Banner(models.Model):
    BANNER_TYPES = (
        ('home', 'Ana Sayfa'),
        ('domestic', 'Yurt İçi Turlar'),
        ('international', 'Yurt Dışı Turlar'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='banners/')
    type = models.CharField(max_length=20, choices=BANNER_TYPES, default='home')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_type_display()} - {self.title}"