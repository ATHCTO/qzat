from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Region(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='المنطقة')
    logo = models.ImageField(upload_to='regions', blank=True, null=True, verbose_name='الشعار')
    
    class Meta:
        verbose_name = 'المنطقة'
        verbose_name_plural = 'المناطق'

    def __str__(self):
        return self.name
    
    
class City(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='المدينة')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='cities', verbose_name='المنطقة')
    
    class Meta:
        verbose_name = 'المدينة'
        verbose_name_plural = 'المدن'
        unique_together = ('region', 'name')

    def __str__(self):
        return f"{self.name} - {self.region.name}"


class Address(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='addresses', verbose_name='المنطقة')
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='addresses', verbose_name='المدينة')
    street = models.CharField(max_length=100, verbose_name='الشارع')
    building_number = models.PositiveSmallIntegerField(null=True, blank=True, validators=[MinValueValidator(1)], verbose_name='رقم المبنى')
    additional_number = models.CharField(max_length=10, null=True, blank=True, verbose_name='الرقم الإضافي')
    postal_code = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(10000), MaxValueValidator(99999)], verbose_name='الرمز البريدي')
    national_address_code = models.CharField(max_length=8, unique=True, null=True, blank=True, help_text='مكون من 4 حروف و 4 أرقام', verbose_name='رمز العنوان الوطني')
    geo_coordinates = models.CharField(max_length=255, null=True, blank=True, verbose_name='الإحداثيات الجغرافية')
    
    class Meta:
        verbose_name = 'العنوان'
        verbose_name_plural = 'العناوين'

    def __str__(self):
        return f"{self.building_number} شارع {self.street} - حي {self.district} - {self.city}"