
from rest_framework import serializers
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
        fields = ['id','username', 'email', 'first_name', 'last_name','telephone' ,'image_url']  

class ClientGenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['username','first_name', 'last_name' ,'image_url']


class MetierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metier
        fields = ['id_metier', 'nom_metier', 'description']


class ProfessionalRequestSerializer(serializers.ModelSerializer):
    metiers = serializers.PrimaryKeyRelatedField(
        queryset=Metier.objects.all(),  
        many=True  
    )

    class Meta:
        model = Professional
        fields = [
            'metiers', 'localisation', 'about_me', 'description_experience',
            'birth_date', 'postal_code', 'image_url'
        ]

    def create(self, validated_data):
        metiers_data = validated_data.pop('metiers')
        professional = Professional.objects.create(**validated_data)
        professional.metiers.set(metiers_data)  

        return professional
    
class ProfessionalSerializer(serializers.ModelSerializer):
    client = ClientSerializer()  
    metiers = MetierSerializer(many=True)
    class Meta:
        model = Professional
        fields = ['id', 'metiers', 'localisation', 'description_experience','about_me' , 'birth_date','postal_code', 'avis_moyenne', 'status','join_date', 'image_url', 'client']

class ProfessionalUpdateSerializer(serializers.ModelSerializer):
    metiers = serializers.PrimaryKeyRelatedField(
        queryset=Metier.objects.all(),
        many=True
    )

    class Meta:
        model = Professional
        fields = ['metiers', 'description_experience', 'about_me', 'localisation', 'image_url']

    def update(self, instance, validated_data):
        metiers_data = validated_data.pop('metiers', None)  
        for attr, value in validated_data.items():
            setattr(instance, attr, value) 
        if metiers_data:
            instance.metiers.set(metiers_data)  
        instance.save()
        return instance
class ProfessionalStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professional
        fields = ['status']


class AvisProfSerializer(serializers.ModelSerializer):
    client = ClientGenSerializer(read_only=True)  
    class Meta:
        model = AvisProf
        fields = ['note','commentaire' , 'date_avis' , 'client']
        read_only_fields = ['client', 'professionnel']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id_notification', 'contenu', 'date_recoi', 'id_receveur']
        read_only_fields = ['id_notification', 'date_recoi']  


class AnnonceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annonce
        fields = ['id_annonce', 'titre', 'contenu', 'vu_par', 'image_url', 'date_publication']
        read_only_fields = ['professionnel']

class MarketownerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marketowner
        fields = ['adresse', 'current_marketplace']  # Exclude 'client' as we handle it in the view

    def create(self, validated_data):
        current_marketplace = validated_data.pop('current_marketplace', None)
        marketowner = Marketowner.objects.create(**validated_data)  # Create without 'current_marketplace'
        
        # Handle the ForeignKey separately
        if current_marketplace:
            marketowner.current_marketplace = current_marketplace
            marketowner.save()

        return marketowner

class MarketplaceSerializer(serializers.ModelSerializer):
    note = serializers.ReadOnlyField()  # Assure que la note dynamique est incluse
    class Meta:
        model = Marketplace
        fields = ['id_marketplace','nom', 'description', 'categories', 'localisation', 'note', 'map']
        # extra_kwargs = {
        #     'note': {'required': False}  
        # }

class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = '__all__'  

class AvisMarketSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    class Meta:
        model = AvisMarket
        fields = ['id_avis', 'marketplace', 'client', 'note', 'commentaire', 'date_created']
        read_only_fields = ['id_avis', 'date_created']

class AnnonceMarketSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnonceMarket
        fields = ['id_annonce', 'titre', 'contenu', 'image_url', 'marketplace', 'vu_par']
        read_only_fields = ['id_annonce', 'vu_par']


class MarketMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketMember
        fields = ['client', 'adresse', 'current_marketplace']
    def create(self, validated_data):
        client = self.context['request'].user.client  # Get the client associated with the logged-in user

        market_member = MarketMember.objects.create(client=client, **validated_data)
        return market_member

class MarketOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marketowner
        fields = ['id_marketowner', 'client', 'adresse', 'current_marketplace', 'join']

class AvisProduitSerializer(serializers.ModelSerializer):
    client = ClientSerializer(read_only=True)
    class Meta:
        model = AvisProduit
        fields = ['id_avis', 'produit', 'client', 'note', 'commentaire', 'date_avis']
        read_only_fields = ['id_avis', 'date_avis', 'produit', 'client']  

class ProduitSerializer(serializers.ModelSerializer):
    marketplace = MarketplaceSerializer(read_only=True)  
    avis = AvisProduitSerializer( many=True, read_only=True) 
    note = serializers.ReadOnlyField()  

    class Meta:
        model = Produit
        fields = ['id_produit', 'nom', 'description', 'prix', 'disponibilite_stock', 
                  'categorie', 'dimension', 'poids', 'materiaux', 'image_url','note', 'marketplace','avis']
        read_only_fields = ['id_produit']



from rest_framework import serializers
from .models import Panier, PanierProduit, Produit

class PanierProduitSerializer(serializers.ModelSerializer):
    produit_nom = serializers.CharField(source='produit.nom')
    produit_image_url = serializers.CharField(source='produit.image_url')
    produit_prix = serializers.DecimalField(source='produit.prix', max_digits=10, decimal_places=2)  # Include product price


    class Meta:
        model = PanierProduit
        fields = ['id', 'produit_nom', 'produit_image_url','produit_prix', 'quantite', 'produit']

class PanierSerializer(serializers.ModelSerializer):
    produits = PanierProduitSerializer(many=True)

    class Meta:
        model = Panier
        fields = ['id', 'client', 'date_creation', 'produits']


class LivraisonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livraison
        fields = [
            'phone_number',
            'country',
            'region',
            'cartier',
            'methode_livraison',
            'adresse_livraison',
            'frais_livraison',
            'date_estime',
        ]

    # Ensure the date_estime is 3 weeks ahead of order date
    def validate_date_estime(self, value):
        from datetime import timedelta
        from django.utils import timezone

        # Assuming the date_estime is provided by the client
        date_estime = timezone.datetime.strptime(value, "%Y-%m-%d").date()
        current_date = timezone.now().date()

        # Add 3 weeks to the current date
        if date_estime < current_date + timedelta(weeks=3):
            raise serializers.ValidationError("Date estimation must be at least 3 weeks after today.")
        return value


from .models import Commande
from .models import Panier
from rest_framework import serializers

class CommandeSerializer(serializers.ModelSerializer):
    livraison = LivraisonSerializer()

    class Meta:
        model = Commande
        fields = ['client', 'panier', 'livraison']

    def create(self, validated_data):
        livraison_data = validated_data.pop('livraison')
        commande = Commande.objects.create(**validated_data)

        # Create the associated Livraison
        Livraison.objects.create(commande=commande, **livraison_data)

        return commande
