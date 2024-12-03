from django.urls import path
from . import views

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
    path('api/annonces/create/', views.create_annonce_view, name='create_annonce'),  # Create an annonce
    path('api/annonces/<int:id_prof>/', views.list_annonces_view, name='list_annonces'),  # List all annonces
    path('api/annonces/<int:annonce_id>/delete/', views.delete_annonce_view, name='delete_annonce'),  # Delete annonce by id
    #rechercher
    path('api/professionals/search/', views.search_professionals, name='search_professionals'),






]
