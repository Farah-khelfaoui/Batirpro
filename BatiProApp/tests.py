from django.test import TestCase

from .models import *

def test_obtenir_details_produit_with_null_poids(self):
    # Create a category instance
    categorie = Categorie.objects.create(nom="Electronics", description="Electronic items")
    
    # Create a product instance with null poids
    produit = Produit.objects.create(
        nom="Laptop",
        description="A high-end gaming laptop",
        prix=1500.00,
        disponibilite_stock=True,
        categorie=categorie,
        dimension="15x10x1 inches",
        poids=None,  # Null value for poids
        materiaux="Aluminum",
        image_url="http://example.com/laptop.jpg",
        avis_moyen=4.5
    )
    
    # Get product details
    details = produit.obtenirDetailsProduit()
    
    # Check if the poids is None in the details
    self.assertIsNone(details["poids"])

def test_obtenir_details_produit_with_null_materiaux(self):
    # Create a category instance
    categorie = Categorie.objects.create(nom="Electronics", description="Electronic items")
    
    # Create a product instance with null materiaux
    produit = Produit.objects.create(
        nom="Smartphone",
        description="A latest model smartphone",
        prix=999.99,
        disponibilite_stock=True,
        categorie=categorie,
        dimension="6x3x0.3 inches",
        poids=0.5,
        materiaux=None,  # Null value for materiaux
        image_url="http://example.com/smartphone.jpg",
        avis_moyen=4.7
    )
    
    # Get product details
    details = produit.obtenirDetailsProduit()
    
    # Check if the materiaux is None in the details
    self.assertIsNone(details["materiaux"])
