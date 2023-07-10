from django.db import models
from django.conf import settings
from django.utils import timezone
# Create your models here.

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
    
    def save(self, *args, **kwargs):
        if self.og_price != self.price:
            self.og_price = self.price
            self.stripe_price = int(self.price * 100)
            self.price_cahnged_timestamp = timezone.now()
            
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return f"/products/{self.handle}"