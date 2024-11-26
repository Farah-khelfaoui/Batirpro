from django.contrib import admin
from .models import  *
admin.site.register(Categorie)
admin.site.register(Produit)
admin.site.register(User)
admin.site.register(Client)
admin.site.register(Metier)
admin.site.register(Annonce)
admin.site.register(Professional)
admin.site.register(AvisProf)
admin.site.register(Notification)
admin.site.register(Message)
# class MarketOwnerAdmin(admin.ModelAdmin):
#     list_display = ['username', 'current_marketplace']
admin.site.register(Marketplace)
admin.site.register(MarketOwner)
admin.site.register(AvisProduit)
admin.site.register(AnnonceMarket)
admin.site.register(Promotion)
admin.site.register(Panier)
admin.site.register(PanierProduit)
admin.site.register(Commande)
admin.site.register(Livraison)
