from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from django.db.models import Q
from ..models import Order
from .serializers import OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from django.contrib.auth import get_user_model

User = get_user_model()


class OrderListCreateView(generics.ListCreateAPIView):
    """
    GET /orders/:
      Gibt eine Liste aller Bestellungen zurück, bei denen der angemeldete Nutzer
      entweder als Kunde (customer_user) oder als Anbieter (business_user) beteiligt ist.
    
    POST /orders/:
      Erlaubt es, eine neue Bestellung basierend auf einem OfferDetail zu erstellen.
      Nur Nutzer mit einem CustomerProfile dürfen Bestellungen erstellen.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(Q(customer_user=user) | Q(business_user=user)).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        if not hasattr(request.user, "profile") or request.user.profile.type != "customer":
            raise PermissionDenied("Nur Kunden können Bestellungen erstellen.")
        
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        read_serializer = OrderSerializer(order, context={'request': request})
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)



class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /orders/{id}/:
      Ruft die Details einer spezifischen Bestellung ab.
    
    PATCH /orders/{id}/:
      Aktualisiert nur den Status einer Bestellung.
      Nur der Ersteller (Kunde) darf den Status ändern.
    
    DELETE /orders/{id}/:
      Löscht eine Bestellung. Nur Admin-Nutzer (Staff) dürfen Bestellungen löschen.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def update(self, request, *args, **kwargs):
      instance = self.get_object()
      
      # Nur der Business User darf den Status ändern
      if instance.business_user != request.user:
          raise PermissionDenied("Nur der Business User darf den Status ändern.")
      
      serializer = OrderStatusUpdateSerializer(instance, data=request.data, partial=True)
      serializer.is_valid(raise_exception=True)
      serializer.save()
      
      read_serializer = OrderSerializer(instance, context={'request': request})
      return Response(read_serializer.data)


    def destroy(self, request, *args, **kwargs):
        if not getattr(request.user, "is_staff", False):
            raise PermissionDenied("Nur Admins dürfen Bestellungen löschen.")
        return super().destroy(request, *args, **kwargs)



class OrderCountView(APIView):
    """
    GET /orders/order-count/{business_user_id}/:
    Gibt die Anzahl der laufenden Bestellungen für einen Business-Nutzer zurück.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, business_user_id):
        business_user = get_object_or_404(User, id=business_user_id)
        order_count = Order.objects.filter(business_user=business_user, status='in_progress').count()
        return Response({"order_count": order_count})


class CompletedOrderCountView(APIView):
    """
    GET /orders/completed-order-count/{business_user_id}/:
    Gibt die Anzahl der abgeschlossenen Bestellungen für einen Business-Nutzer zurück.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get(self, request, business_user_id):
        business_user = get_object_or_404(User, id=business_user_id)
        completed_order_count = Order.objects.filter(business_user=business_user, status='completed').count()
        return Response({"completed_order_count": completed_order_count})