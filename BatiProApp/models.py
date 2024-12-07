from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model


class User(AbstractUser):
    pass

class Client(User):
    telephone = models.CharField(max_length=20)
    image_url = models.URLField(max_length=500, blank=True, null=True)

    class Meta:
        db_table = 'clients'

    def creerCompte(self):
        pass
    def __str__(self):
        return f"{self.username} - {self.email}"

    def supprimerCompte(self):
        self.delete()

class Metier(models.Model):
    id_metier = models.AutoField(primary_key=True)
    nom_metier = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.nom_metier
    

class Professional(models.Model):
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='professional' , null=True)
    metiers = models.ManyToManyField(Metier, related_name='professionals')  
    localisation = models.CharField(max_length=500)
    about_me = models.TextField(default='I am BatiPro Professional')
    description_experience = models.TextField()
    birth_date = models.DateField(null=True)
    postal_code = models.CharField(max_length=5 , default='', blank=True)
    avis_moyenne = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    status = models.CharField(max_length=50, default='en attente')
    join_date = models.DateField(auto_now_add=True, null=True)
    
    image_url = models.URLField(max_length=500, blank=True, null=True)
    class Meta:
        db_table = 'Professionals'
    def __str__(self):
        return f"{self.client}"
    def avis_moyenne(self):
        """Retourne la moyenne des avis pour ce professionnel."""
        avis = AvisProf.objects.filter(professionnel=self)
        if avis.exists():
            return sum([a.note for a in avis]) / len(avis)
        return 0.0




class Message(models.Model):
    id_message = models.AutoField(primary_key=True)
    expediteur_id = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='messages_sent')
    destinateur_id = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='messages_received')
    contenu = models.TextField()
    date_envoi = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'messages'  # Specify the database table name

    def __str__(self):
        return f"{self.expediteur_id.username} to {self.destinateur_id.username}: {self.contenu[:20]}..."


class AvisProf(models.Model):
    id_avis = models.AutoField(primary_key=True)  # Automatically incrementing primary key
    professionnel = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name='avisProf')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='avisClient')
    note = models.DecimalField(max_digits=1, decimal_places=0)  # Assuming note is a number from 0 to 9
    date_avis = models.DateField(auto_now_add=True)  # Automatically set to the current date when created
    commentaire = models.TextField(blank=True, null=True)  # Optional field for the comment

    class Meta:
        db_table = 'avisProf'
        unique_together = ['professionnel', 'client']  

    def __str__(self):
        return f"Avis by {self.client.username} for {self.professionnel.client.username} - Note: {self.note}"
    
class Annonce(models.Model):
    id_annonce = models.AutoField(primary_key=True)
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    professionnel = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name='annonces')
    vu_par = models.IntegerField(default=0)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    date_publication = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titre} par {self.professionnel.client.username}"
    

class Notification(models.Model):
    id_notification = models.AutoField(primary_key=True)
    contenu = models.TextField() 
    date_recoi = models.DateField(auto_now_add=True)  
    id_receveur = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='notifications')

    class Meta:
        db_table = 'notifications' 

    def __str__(self):
        return f"Notification {self.id_notification} for {self.id_receveur.username}"


class Categorie(models.Model):

    id_categorie = models.AutoField(primary_key=True)  
    nom = models.CharField(max_length=255 , unique=True)  
    description = models.TextField()  


    def __str__(self):
        return self.nom  


class Produit(models.Model):
    id_produit = models.AutoField(primary_key=True) 
    marketplace = models.ForeignKey('Marketplace', on_delete=models.CASCADE , related_name='produits' ,null=True)
    nom = models.CharField(max_length=255) 
    description = models.TextField()  
    prix = models.DecimalField(max_digits=10, decimal_places=2) 
    disponibilite_stock = models.IntegerField(default=0)  
    categorie = models.ForeignKey(Categorie, related_name='produits', on_delete=models.SET_NULL , null=True)  
    dimension = models.CharField(max_length=255) 
    poids = models.FloatField()  
    materiaux = models.CharField(max_length=255)  
    image_url = models.URLField(max_length=200)  
  

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['nom', 'marketplace'], name='unique_product_in_marketplace')
        ]
    def note(self):
        average = self.avis.aggregate(avg_note=Avg('note'))['avg_note']
        return round(average, 1) if average else 0.0  # Retourne 0.0 si aucun avis n'existe

    def __str__(self):
        return self.nom 

class AvisProduit(models.Model):
    id_avis = models.AutoField(primary_key=True) 
    produit = models.ForeignKey('Produit', on_delete=models.CASCADE, related_name='avis') 
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='avis_produit') 
    note = models.DecimalField(max_digits=1, decimal_places=0)  # Rating (0-9)
    date_avis = models.DateField(auto_now_add=True)  
    commentaire = models.TextField(blank=True, null=True)  

    class Meta:
        db_table = 'avis_produit'
        unique_together = ['produit', 'client']  # Ensures a client can review a product only once

    def __str__(self):
        return f"Avis by {self.client.username} for {self.produit.nom} - Note: {self.note}"
    
from django.db.models import Avg
class Marketplace(models.Model):
    id_marketplace = models.AutoField(primary_key=True)  # Automatically incrementing primary key
    nom = models.CharField(max_length=100,unique=True)
    description = models.TextField()
    categories = models.ManyToManyField(Categorie, related_name='marketplaces')
    localisation = models.CharField(max_length=255)
    map = models.CharField(default='', max_length=1000)
    status = models.CharField(max_length=255, default='pending ...')
    members = models.ManyToManyField('MarketMember', related_name='marketplaces') 
    @property
    def note(self):
        average = self.avis.aggregate(avg_note=Avg('note'))['avg_note']
        return round(average, 1) if average else 0.0  # Retourne 0.0 si aucun avis n'existe

    def __str__(self):
        return self.nom


class Marketowner(models.Model):
    id_marketowner = models.AutoField(primary_key=True) 
    join = models.DateField(auto_now_add=True, null=True)
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='Marketowner',null=True)
    adresse = models.CharField(max_length=255)
    current_marketplace = models.ForeignKey(Marketplace, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.client.username
    class Meta:
        db_table = 'marketowners'

class MarketMember(models.Model):
    id_member = models.AutoField(primary_key=True)
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='market_member', null=True)
    adresse = models.CharField(max_length=255)
    current_marketplace = models.ForeignKey(Marketplace, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.client.username} - {self.adresse}"

    class Meta:
        db_table = 'market_members'

class AvisMarket(models.Model):
    id_avis = models.AutoField(primary_key=True)
    marketplace = models.ForeignKey(Marketplace, on_delete=models.CASCADE, related_name='avis')
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    note = models.DecimalField(max_digits=2, decimal_places=1)
    commentaire = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'avis_market'
        unique_together = ('marketplace', 'client')  # Un client ne peut laisser qu'un avis par marketplace


class AnnonceMarket(models.Model):
    id_annonce = models.AutoField(primary_key=True)
    titre = models.CharField(max_length=255)
    contenu = models.TextField()
    marketplace = models.ForeignKey(Marketplace, on_delete=models.CASCADE, related_name='annonces')
    vu_par = models.IntegerField(default=0) 
    image_url = models.CharField(max_length=255)
    date_created = models.DateField(auto_now_add=True, null=True)

    def __str__(self):
        return self.titre

from datetime import date

class Promotion(AnnonceMarket):
    id_promotion = models.AutoField(primary_key=True)
    produit = models.ForeignKey('Produit', on_delete=models.CASCADE, related_name='promotions')  
    pourcentage = models.IntegerField() 
    date_debut = models.DateField()
    date_fin = models.DateField()

    def __str__(self):
        return f"Promotion: {self.titre} - {self.pourcentage}% Off"
    class Meta:
        db_table = 'promotions'

    def is_active(self):
        today = date.today()
        return self.date_debut <= today <= self.date_fin

''' _________________________________________________'''
class Panier(models.Model):
    client = models.ForeignKey(Client, related_name='paniers', on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Panier de {self.client.username} "

class PanierProduit(models.Model):
    panier = models.ForeignKey(Panier, related_name='produits', on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, related_name='paniers', on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom}"

class Commande(models.Model):
    client = models.ForeignKey(Client, related_name='commandes', on_delete=models.CASCADE)
    panier = models.OneToOneField(Panier, related_name='commande', on_delete=models.CASCADE)
    date_commande = models.DateField(auto_now_add=True)
    statut = models.CharField(max_length=50, default='en attente')  # Statut: en attente, validée, expédiée...
    def total(self):
        """Calculates the total price of all products in the panier."""
        total = 0
        if self.panier.produits.all() == None:
            total =  0.0
        else:
            for panier_produit in self.panier.produits.all():
                total += panier_produit.produit.prix * panier_produit.quantite
        return total

    def __str__(self):
        return f"Commande de {self.client.username} - {self.id}"

class Livraison(models.Model):
    commande = models.OneToOneField(Commande, related_name='livraison', on_delete=models.CASCADE)
    date_estime = models.DateField()
    methode_livraison = models.CharField(max_length=20)  # "standard", "express", etc.
    adresse_livraison = models.CharField(max_length=100)
    frais_livraison = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=50, default='en préparation')  # "en préparation", "expédiée", "livrée", etc.
    def total(self):
        return self.frais_livraison+self.commande.total()
    def __str__(self):
        return f"Livraison {self.commande.id} - {self.statut}"

