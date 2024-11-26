from rest_framework import serializers
from .models import Produit, Categorie , Metier
from .models import *



class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Create the User instance
        user = User.objects.create_user(**validated_data)


        return user


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['telephone']


class ProfessionalRequestSerializer(serializers.ModelSerializer):
    metiers = serializers.PrimaryKeyRelatedField(
        queryset=Metier.objects.all(),  # Allow selecting existing Metier objects
        many=True  # Since it's a many-to-many field
    )

    class Meta:
        model = Professional
        fields = ['metiers', 'localisation', 'description_experience', 'image_url']

    def create(self, validated_data):
        metiers_data = validated_data.pop('metiers')
        professional = Professional.objects.create(**validated_data)
        professional.metiers.set(metiers_data)  # Set the many-to-many relationship
        return professional
    


class ProfessionalSerializer(serializers.ModelSerializer):
    client_username = serializers.CharField(source='client.user.username', read_only=True)
    client_first_name = serializers.CharField(source='client.user.first_name', read_only=True)
    client_last_name = serializers.CharField(source='client.user.last_name', read_only=True)
    client_email = serializers.EmailField(source='client.user.email', read_only=True)

    class Meta:
        model = Professional
        fields = ['id', 'client_username', 'client_first_name', 'client_last_name', 'client_email',
                  'metiers', 'localisation', 'description_experience', 'avis_moyenne', 'status', 'image_url']

class ProfessionalStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professional
        fields = ['status']




class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = '__all__'  #  ['id_categorie', 'nom', 'description']

class ProduitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produit
        fields = '__all__'  # ['id_produit', 'nom', 'description', 'prix', 'categorie']


class MetrierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metier
        fields = '__all__'
        