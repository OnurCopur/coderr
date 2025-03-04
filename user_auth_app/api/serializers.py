from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from ..models import Profile

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    repeated_password = serializers.CharField(write_only=True, required=True)
    type = serializers.CharField(write_only=True, required=True)  

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'repeated_password', 'type') 

    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError({"password": "Passwörter stimmen nicht überein."})
        return data

    def create(self, validated_data):
        validated_data.pop('repeated_password')  # Entferne das wiederholte Passwort
        role = validated_data.pop('type')  # Ersetze "type" durch "role"
        user = User.objects.create_user(**validated_data)  # Erstelle den User
        user.role = role  # Setze die Rolle des Users
        user.save()  # Speichere den User

        # Token für den User erstellen
        token = Token.objects.create(user=user)

        return user


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)  # Fügt den Benutzernamen hinzu

    class Meta:
        model = Profile
        fields = ['user', 'username', 'first_name', 'last_name', 'email', 'file', 
                  'location', 'tel', 'description', 'working_hours', 'type', 'created_at']

