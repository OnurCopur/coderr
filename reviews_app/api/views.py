from rest_framework import generics, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from ..models import Review
from .serializers import (
    ReviewSerializer, 
    ReviewCreateSerializer, 
    ReviewUpdateSerializer
)

class ReviewListCreateView(generics.ListCreateAPIView):
    """
    GET /api/reviews/:
      Listet alle Bewertungen. Unterstützt die Filterung über die Query-Parameter:
      - business_user_id: Filtert nach der ID des Geschäftsbenutzers.
      - reviewer_id: Filtert nach der ID des Bewerters.
      - ordering: Sortiert die Ergebnisse nach 'updated_at' oder 'rating'.
    
    POST /api/reviews/:
      Erstellt eine neue Bewertung für einen Geschäftsbenutzer.
      Nur authentifizierte Benutzer mit einem Kundenprofil dürfen Bewertungen erstellen.
      Ein Benutzer kann pro Geschäftsbenutzer nur eine Bewertung abgeben.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['updated_at', 'rating']
    ordering = ['-updated_at']

    def get_queryset(self):
        queryset = Review.objects.all()
        business_user_id = self.request.query_params.get('business_user_id')
        reviewer_id = self.request.query_params.get('reviewer_id')
        if business_user_id:
            queryset = queryset.filter(business_user__id=business_user_id)
        if reviewer_id:
            queryset = queryset.filter(reviewer__id=reviewer_id)
        return queryset

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ReviewCreateSerializer
        return ReviewSerializer

    def perform_create(self, serializer):
        # Nur Kunden dürfen Bewertungen erstellen.
        if not hasattr(self.request.user, "profile") or self.request.user.profile.type != "customer":
            raise PermissionDenied("Nur authentifizierte Kunden können Bewertungen erstellen.")
        serializer.save()

class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/reviews/{id}/:
      Ruft die Details einer spezifischen Bewertung ab.
    
    PATCH /api/reviews/{id}/:
      Aktualisiert ausgewählte Felder ('rating' und 'description') einer bestehenden Bewertung.
      Nur der Ersteller der Bewertung darf diese bearbeiten.
    
    DELETE /api/reviews/{id}/:
      Löscht eine spezifische Bewertung.
      Nur der Ersteller der Bewertung darf diese löschen.
    """
    queryset = Review.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ['PATCH', 'PUT']:
            return ReviewUpdateSerializer
        return ReviewSerializer

    def perform_update(self, serializer):
        # Nur der Ersteller (reviewer) darf die Bewertung aktualisieren.
        if self.get_object().reviewer != self.request.user:
            raise PermissionDenied("Sie sind nicht berechtigt, diese Bewertung zu bearbeiten.")
        serializer.save()

    def perform_destroy(self, instance):
        # Nur der Ersteller (reviewer) darf die Bewertung löschen.
        if instance.reviewer != self.request.user:
            raise PermissionDenied("Sie sind nicht berechtigt, diese Bewertung zu löschen.")
        instance.delete()
