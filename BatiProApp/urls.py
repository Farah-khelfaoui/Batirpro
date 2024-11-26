from django.urls import path
from . import views

urlpatterns = [
    # User authentication and registration endpoints
    path('api/register/', views.register_view, name='register'),
    path('api/login/', views.login_view, name='login'),
    path('api/logout/', views.logout_view, name='logout'),

    # Client update endpoint
    path('api/client-update/', views.update_client_view, name='update_client'),
    #to get all profs
    path('api/professionals/', views.list_professionals, name='list_professionals'),
    # Professional request endpoint
    path('api/professional-request/', views.request_professional_view, name='request_professional'),

    # Admin-only professional management endpoints
    path('api/professionals-pending/', views.list_pending_professionals, name='list_pending_professionals'),
    path('api/professionals/<int:pk>/update_status/', views.update_professional_status, name='update_professional_status'),

    # Home page endpoint
    path('', views.home, name='home'),  # Serves the home template at the root URL
    path('del/', views.dele, name='del'),  # Serves the home template at the root URL
]
