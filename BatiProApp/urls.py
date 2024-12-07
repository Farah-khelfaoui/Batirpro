from django.urls import path
from . import views
from .views import *

urlpatterns = [
    # User authentication and registration endpoints
    path('api/register/', views.register_view, name='register'),
    path('api/login/', views.login_view, name='login'),
    path('api/logout/', views.logout_view, name='logout'),

    # Client update endpoint
    path('api/client-update/', views.update_client_view, name='update_client'),
    path('api/clients/', views.list_clients, name='list_clients'),

    # Metiers
    path('api/metiers/', views.list_metiers, name='list_metiers'),
    path('api/metiers/<int:pk>/', views.get_metier_detail , name='get_metier_detail'),

    #to get all profs
    path('api/professionals/', views.list_professionals, name='list_professionals'),
    path('api/professionals/<int:pk>/', views.get_professional_detail, name='get_professional_detail'),

    # Professional request endpoint
    path('api/professional-request/', views.request_professional_view, name='request_professional'),
    path('api/professional/update/', views.update_professional_profile_view, name='update_professional_profile'),

    # Admin-only professional management endpoints
    path('api/professionals-pending/', views.list_pending_professionals, name='list_pending_professionals'),
    path('api/professionals/<int:pk>/update_status/', views.update_professional_status, name='update_professional_status'),

    # URL to list all reviews for a professional or Create new one 
    path('api/professionals/<int:prof_id>/review/', views.create_avis_view, name='create_avis'),
    path('api/professionals/<int:prof_id>/reviews/', views.list_avis_view, name='list_avis'),

    #notifications
    path('api/notifications/', views.list_notifications_view, name='list_notifications'),
    path('api/notification/create/', views.create_notification_view, name='create_notification'),

    #annonces
    path('api/annonces/create/', views.create_annonce_view, name='create_annonce'), 
    path('api/annonces/<int:id_prof>/', views.list_annonces_view, name='list_annonces'),  
    path('api/annonces/<int:annonce_id>/delete/', views.delete_annonce_view, name='delete_annonce'),  
    #rechercher
    path('api/professionals/search/', views.search_professionals, name='search_professionals'),
    
    
    path('api/home/products/', views.list_products_home, name='home_products'),
    # path('api/professionals/search/', views.search_professionals, name='search_professionals'),


    path('api/market_member/create/', views.create_market_member, name='create_market_member'),
    path('api/marketplace/create/', views.create_marketplace, name='create-marketplace'),
    path('api/marketplace/pending/', views.get_pending_marketplaces, name='get-pending-marketplaces'),
    path('api/marketplace/<int:pk>/status/', views.update_marketplace_status, name='update-marketplace-status'),
    path('api/marketplace/<int:marketplace_id>/add_member/', views.add_market_member, name='add-market-member'),

    path('api/marketplaces/', MarketPlaces, name='marketplace-list'),
    path('api/marketplaces/<int:pk>/', MarketplaceDetail, name='marketplace-detail'),

    path('api/marketplace/<int:marketplace_id>/add-avis/', add_avis, name='add-avis'),
    path('api/marketplace/<int:marketplace_id>/add-annonce/', add_annonce, name='add-annonce'),

    path('api/products/', views.list_products, name='product-list'),  
    path('api/products/create/', views.create_product, name='product-create'), 
    path('api/products/<int:pk>/update/', views.update_product, name='product-update'), 
    path('api/products/<int:pk>/delete/', views.delete_product, name='product-delete'), 
    path('api/produits/<int:produit_id>/avis/', views.add_product_review, name='add_product_review'),
    path('api/search_products/', views.search_products, name='search-products'),
]
