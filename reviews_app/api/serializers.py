from rest_framework import serializers
from ..models import Review
from django.contrib.auth import get_user_model

User = get_user_model()

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            'id',
            'business_user',
            'reviewer',
            'rating',
            'description',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'reviewer', 'created_at', 'updated_at']

class ReviewCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['business_user', 'rating', 'description']

    def validate_business_user(self, value):
        # Sicherstellen, dass der angegebene User ein Geschäftsbenutzer ist
        if not hasattr(value, 'profile') or value.profile.type != 'business':
            raise serializers.ValidationError("Eine Bewertung kann nur für einen Geschäftsbenutzer abgegeben werden.")
        return value

    def validate(self, data):
        request = self.context.get("request")
        reviewer = request.user
        business_user = data.get("business_user")
        if Review.objects.filter(business_user=business_user, reviewer=reviewer).exists():
            raise serializers.ValidationError("Sie haben für diesen Geschäftsbenutzer bereits eine Bewertung abgegeben.")
        return data

    def create(self, validated_data):
        request = self.context.get("request")
        reviewer = request.user
        return Review.objects.create(reviewer=reviewer, **validated_data)

class ReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['rating', 'description']
