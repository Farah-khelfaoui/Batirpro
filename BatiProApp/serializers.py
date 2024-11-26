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
    avis_moyenne = serializers.SerializerMethodField()  

    class Meta:
        model = Professional
        fields = '__all__'  # Include all fields from the model + avis_moyenne

    def get_avis_moyenne(self, obj):
        """Calculate the average review for this professional."""
        avis = AvisProf.objects.filter(professional=obj)
        if avis.exists():
            return round(sum([a.note for a in avis]) / avis.count(), 2)
        return 0.0

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
        