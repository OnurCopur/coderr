from rest_framework import serializers
from rest_framework.reverse import reverse
from ..models import Offer, OfferDetail

class OfferDetailSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']

    def get_url(self, obj):
        request = self.context.get("request")
        return reverse("offer-detail-detail", args=[obj.id], request=request)


class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            'id',
            'user',
            'title',
            'image',
            'description',
            'created_at',
            'updated_at',
            'details',
            'min_price',
            'min_delivery_time',
            'user_details'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at', 'min_price', 'min_delivery_time', 'user_details']

    def get_min_price(self, obj):
        mp = obj.min_price()
        return mp if mp is not None else 0

    def get_min_delivery_time(self, obj):
        mdt = obj.min_delivery_time()
        return mdt if mdt is not None else 0

    def get_user_details(self, obj):
        user = obj.user
        return {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
        }

    def validate_details(self, value):
        if len(value) != 3:
            raise serializers.ValidationError("Exactly three offer details must be provided.")
        types = [detail['offer_type'] for detail in value]
        required_types = {'basic', 'standard', 'premium'}
        if set(types) != required_types:
            raise serializers.ValidationError("Offer details must include one each of basic, standard, and premium.")
        for detail in value:
            features = detail.get('features')
            if not features or not isinstance(features, list) or len(features) == 0:
                raise serializers.ValidationError("Each offer detail must have at least one feature.")
        return value

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        user = self.context['request'].user
        offer = Offer.objects.create(user=user, **validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        instance.title = validated_data.get('title', instance.title)
        instance.image = validated_data.get('image', instance.image)
        instance.description = validated_data.get('description', instance.description)
        instance.status = validated_data.get('status', instance.status)
        instance.save()

        if details_data:
            for detail_data in details_data:
                offer_type = detail_data.get('offer_type')
                try:
                    detail = instance.details.get(offer_type=offer_type)
                    detail.title = detail_data.get('title', detail.title)
                    detail.revisions = detail_data.get('revisions', detail.revisions)
                    detail.delivery_time_in_days = detail_data.get('delivery_time_in_days', detail.delivery_time_in_days)
                    detail.price = detail_data.get('price', detail.price)
                    detail.features = detail_data.get('features', detail.features)
                    detail.save()
                except OfferDetail.DoesNotExist:
                    pass

        return instance
