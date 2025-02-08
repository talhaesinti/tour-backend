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
        Region kaydedilirken slug otomatik olarak oluşturulur ve unique olmasını sağlar.
        Aktiflik değişimi varsa bağlı InternationalTour'ları günceller.
        """
        # Eğer slug boşsa otomatik olarak oluştur
        if not self.slug:
            unique_slug = slugify(self.name)
            while Region.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f"{slugify(self.name)}-{self.pk or Region.objects.latest('id').id + 1}"
            self.slug = unique_slug

        # Aktiflik değişimi varsa bağlı InternationalTour'ları güncelle
        if self.pk:
            old_instance = Region.objects.filter(pk=self.pk).first()
            if old_instance and old_instance.is_active != self.is_active:
                from .models import InternationalTour
                InternationalTour.objects.filter(region=self).update(is_active=self.is_active)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Region silinirken bağlı turları pasif yapar.
        """
        from .models import InternationalTour
        InternationalTour.objects.filter(region=self).update(is_active=False)
        super().delete(*args, **kwargs)


class DomesticTour(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
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

    def save(self, *args, **kwargs):
        """
        DomesticTour kaydedilirken slug otomatik olarak oluşturulur ve unique olmasını sağlar.
        """
        if not self.slug:
            unique_slug = slugify(self.name)
            while DomesticTour.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f"{slugify(self.name)}-{self.pk or DomesticTour.objects.latest('id').id + 1}"
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class InternationalTour(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    airline = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    tour_info = models.TextField()
    tour_program_pdf = models.FileField(upload_to='tour_programs/', blank=True, null=True)
    region = models.ForeignKey('Region', on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    thumbnail = models.ImageField(upload_to='thumbnails/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """
        InternationalTour kaydedilirken slug otomatik olarak oluşturulur ve unique olmasını sağlar.
        """
        if not self.slug:
            unique_slug = slugify(self.name)
            while InternationalTour.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f"{slugify(self.name)}-{self.pk or InternationalTour.objects.latest('id').id + 1}"
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class DomesticTourImage(models.Model):
    tour = models.ForeignKey('DomesticTour', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='domestic_tour_images/')
    caption = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.tour.name} - Image"


class InternationalTourImage(models.Model):
    tour = models.ForeignKey('InternationalTour', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='international_tour_images/')
    caption = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.tour.name} - Image"

class Banner(models.Model):
    BANNER_TYPES = (
        ('home', 'Ana Sayfa'),
        ('domestic', 'Yurt İçi Turlar'),
        ('international', 'Yurt Dışı Turlar'),
        ('contact', 'İletişim'),
        ('about', 'Hakkımızda'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='banners/')
    type = models.CharField(max_length=20, choices=BANNER_TYPES, default='home')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_type_display()} - {self.title}"