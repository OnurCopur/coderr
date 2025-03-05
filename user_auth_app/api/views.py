from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import RegistrationSerializer

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from django.contrib.auth import authenticate
from rest_framework.views import APIView

from django.shortcuts import get_object_or_404
from ..models import Profile
from .serializers import ProfileSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication


User = get_user_model()

class RegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        # Erstelle den User
        response = super().create(request, *args, **kwargs)

        # Hole den User
        user = User.objects.get(username=response.data['username'])

        # Erstelle automatisch ein Profil für den Benutzer und speichere die E-Mail im Profil
        Profile.objects.create(user=user, email=user.email)

        # Überprüfe, ob bereits ein Token für den User existiert
        token, created = Token.objects.get_or_create(user=user)

        # Füge das Token zu den Antwortdaten hinzu
        response.data['token'] = token.key

        return Response(response.data)




class CustomLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        # Authentifiziere den User mit den übergebenen Daten
        user = authenticate(username=username, password=password, email=email)

        if user:
            # Token erstellen oder holen
            token, _ = Token.objects.get_or_create(user=user)

            # Erfolgreiche Antwort mit Token und User-Details
            return Response({
                'token': token.key,
                'user_id': user.id,  
                'username': user.username,
                'email': user.email,
                'role': getattr(user, 'role', 'user')  
            }, status=status.HTTP_200_OK)
        
        # Fehlerfall, wenn die Anmeldedaten nicht stimmen
        return Response({"error": "Ungültige Anmeldedaten"}, status=status.HTTP_400_BAD_REQUEST)


class GuestLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        guest_type = request.data.get('type')  # 'customer' oder 'business'

        if guest_type == 'customer':
            username, password = "andrey", "asdasd"
        elif guest_type == 'business':
            username, password = "kevin", "asdasd24"
        else:
            return Response({"error": "Ungültiger Gast-Typ"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user_id': user.id, 'username': user.username, 'role': user.role})
        return Response({"error": "Ungültige Anmeldedaten"}, status=status.HTTP_400_BAD_REQUEST)


class ProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]


    def get(self, request, pk, format=None):
        if not request.user.is_authenticated:
            return Response({"detail": "User not authenticated"}, status=status.HTTP_403_FORBIDDEN)

        try:
            profile = Profile.objects.get(user_id=pk)
        except Profile.DoesNotExist:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        try:
            profile = Profile.objects.get(user_id=pk)
        except Profile.DoesNotExist:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk, format=None):  # Füge die PATCH-Methode hinzu
        try:
            profile = Profile.objects.get(user_id=pk)
        except Profile.DoesNotExist:
            return Response({"detail": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProfileSerializer(profile, data=request.data, partial=True)  # PATCH erlaubt partielle Updates
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BusinessProfileListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        business_profiles = Profile.objects.filter(type='business')
        serializer = ProfileSerializer(business_profiles, many=True)
        return Response(serializer.data)


class CustomerProfileListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        customer_profiles = Profile.objects.filter(type='customer')
        serializer = ProfileSerializer(customer_profiles, many=True)
        return Response(serializer.data)

