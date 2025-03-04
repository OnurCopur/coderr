from django.db import models
from django.conf import settings

class Review(models.Model):
    business_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='business_reviews'
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='given_reviews'
    )
    rating = models.IntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('business_user', 'reviewer')  # Ein Reviewer kann pro Geschäftsbenutzer nur eine Bewertung abgeben

    def __str__(self):
        return f"Review {self.id} by {self.reviewer} for {self.business_user}"
