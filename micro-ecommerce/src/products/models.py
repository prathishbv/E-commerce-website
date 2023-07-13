from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
import pathlib

# Create your models here.

PROTECTED_MEDIA_ROOT = settings.PROTECTED_MEDIA_ROOT
protected_storage = FileSystemStorage(location=str(PROTECTED_MEDIA_ROOT))

class Product(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=9.99)
    og_price = models.DecimalField(max_digits=10, decimal_places=2, default=9.99)
    handle = models.SlugField(unique=True)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    price_cahnged_timestamp = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    stripe_price = models.IntegerField(default=999)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    @property
    def display_name(self):
        return self.name
    
    def __str__(self):
        return self.display_name
    
    def save(self, *args, **kwargs):
        if self.og_price != self.price:
            self.og_price = self.price
            self.stripe_price = int(self.price * 100)
            self.price_cahnged_timestamp = timezone.now()
            
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse("products:detail", kwargs={"handle": self.handle})
    
    def get_manage_url(self):
        return reverse("products:manage", kwargs={"handle": self.handle})
    
    
def handle_product_attachment_upload(instance, filename):
    return f"products/{instance.product.handle}/attachment/{filename}"

class ProductAttachment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    file = models.FileField(upload_to=handle_product_attachment_upload, storage=protected_storage)
    name = models.CharField(max_length=120, blank=True, null=True)
    is_free = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.name:
            self.name = pathlib.Path(self.file.name).name
        super().save(*args, **kwargs)
    
    @property
    def display_name(self):
        return self.name or pathlib.Path(self.file.name).name
    
    def get_download_url(self):
        return reverse("products:download", kwargs={"handle": self.product.handle, "pk": self.pk})