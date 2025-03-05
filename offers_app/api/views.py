from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Offer, OfferDetail
from .serializers import OfferSerializer, OfferDetailSerializer
from .pagination import OfferPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser


class OfferListCreateView(generics.ListCreateAPIView):
    queryset = Offer.objects.all().order_by('-updated_at')
    serializer_class = OfferSerializer
    # permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    pagination_class = OfferPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # Ermöglicht die Suche in title und description:
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at']  # Für min_price müsste man annotieren
    parser_classes = (JSONParser, MultiPartParser, FormParser)  # Multipart-Parser für Bilder

    def get_queryset(self):
        qs = super().get_queryset()
        creator_id = self.request.query_params.get('creator_id')
        min_price = self.request.query_params.get('min_price')
        max_delivery_time = self.request.query_params.get('max_delivery_time')
        status = self.request.query_params.get('status')  # NEU

        if creator_id:
            qs = qs.filter(user__id=creator_id)
        
        from django.db.models import Min
        qs = qs.annotate(min_price_val=Min('details__price'), min_delivery_time_val=Min('details__delivery_time_in_days'))

        if min_price:
            qs = qs.filter(min_price_val__gte=min_price)
        if max_delivery_time:
            qs = qs.filter(min_delivery_time_val__lte=max_delivery_time)
        if status:  # NEU
            qs = qs.filter(status=status)

        return qs


    def perform_create(self, serializer):
        if self.request.user.profile.type != 'business':
            raise PermissionDenied("Only business users can create offers.")
        
        serializer.save(user=self.request.user)  # Explizit den User setzen




class OfferDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_object(self):
        offer = super().get_object()
        print(f"Anfrage von: {self.request.user} für Offer von {offer.user}")
        if self.request.method in ['PATCH', 'PUT', 'DELETE']:
            if not (self.request.user.is_staff or offer.user == self.request.user):
                raise PermissionDenied("You do not have permission to modify this offer.")
        return offer



class OfferDetailDetailView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
