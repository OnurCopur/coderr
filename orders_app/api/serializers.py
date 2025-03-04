from rest_framework import serializers
from ..models import Order
from offers_app.models import OfferDetail  # Wir gehen davon aus, dass die Offers-App existiert

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id',
            'customer_user',
            'business_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'customer_user',
            'business_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            'status',
            'created_at',
            'updated_at'
        ]


class OrderCreateSerializer(serializers.Serializer):
    offer_detail_id = serializers.IntegerField()

    def validate_offer_detail_id(self, value):
        try:
            offer_detail = OfferDetail.objects.get(id=value)
        except OfferDetail.DoesNotExist:
            raise serializers.ValidationError("Ungültige OfferDetail ID.")
        return value

    def create(self, validated_data):
        offer_detail_id = validated_data['offer_detail_id']
        # Hole das OfferDetail aus der Offers-App
        offer_detail = OfferDetail.objects.get(id=offer_detail_id)
        request = self.context.get('request')
        customer_user = request.user

        # Das zugehörige Angebot (Offer) enthält den Anbieter (business_user)
        business_user = offer_detail.offer.user

        # Übernehme die Felder aus dem OfferDetail
        order = Order.objects.create(
            customer_user=customer_user,
            business_user=business_user,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
            status='in_progress'
        )
        return order


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']
