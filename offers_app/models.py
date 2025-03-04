from django.db import models
from django.conf import settings

class Offer(models.Model):
    STATUS_CHOICES = (
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='offers')
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='offer_images/', blank=True, null=True)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def min_price(self):
        details = self.details.all()
        if details.exists():
            return min(detail.price for detail in details)
        return None

    def min_delivery_time(self):
        details = self.details.all()
        if details.exists():
            return min(detail.delivery_time_in_days for detail in details)
        return None

    def __str__(self):
        return f"{self.title} - {self.status}"


class OfferDetail(models.Model):
    OFFER_TYPE_CHOICES = (
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    )

    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='details')
    title = models.CharField(max_length=255)
    revisions = models.IntegerField()  # -1 steht für "unendlich Revisionen"
    delivery_time_in_days = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField()  # Liste von Features (z. B. ["Logo Design", "Visitenkarte"])
    offer_type = models.CharField(max_length=20, choices=OFFER_TYPE_CHOICES)

    def __str__(self):
        return f"{self.title} ({self.offer_type})"
