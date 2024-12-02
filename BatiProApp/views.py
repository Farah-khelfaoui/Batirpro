from django.shortcuts import render,HttpResponse
from .models import *
from rest_framework import generics , status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated , AllowAny, IsAdminUser
from rest_framework.authtoken.models import Token 
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import *



@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    # Create a serializer for the user registration
    serializer = UserRegistrationSerializer(data=request.data)

    if serializer.is_valid():
        # Save the user instance
        user = serializer.save()
# Create the Client linked to the user
        Client.objects.create(user_ptr=user,
                              username =user.username,
                              email = user.email)  # Client automatically linked to the User
        user.set_password(request.data['password'])
        user.save()
        return Response({'message': 'User registered successfully, and client created'})

    return Response(serializer.errors, status=400)



@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({'message': 'Login successful', 'token': token.key})
    else:
        return Response({'error': 'Invalid credentials'}, status=401)

# Logout View
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    # Get the user's token and delete it
    try:
        request.user.auth_token.delete()
        return Response({'message': 'User logged out successfully'}, status=200)
    except Exception as e:
        return Response({'error': str(e)}, status=400)


# Update client information (phone number)
@api_view(['POST','PUT'])
@permission_classes([IsAuthenticated])
def update_client_view(request):
    client = Client.objects.get(pk=request.user.pk)
    print(client)
    print(request.data)

    serializer = ClientSerializer(client, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        print(serializer.data)

        return Response({'message': 'Client updated successfully'})
    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_professional_view(request):
    # Ensure the current user is a Client and not already a Professional
    if Professional.objects.filter(client=request.user.client).exists():
        return Response({'error': 'You are already a professional'}, status=400)
    
    # Extract client-specific fields from the request data
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    telephone = request.data.get('telephone')

    serializer = ProfessionalRequestSerializer(data=request.data)
    if serializer.is_valid():
        # Update client fields if provided
        client = request.user.client 
        if first_name:
            client.first_name = first_name
        if last_name:
            client.last_name = last_name
        if telephone:
            client.telephone = telephone
        client.save()  

        # Create a professional instance linked to the current user
        professional = Professional.objects.create(
            client=client,
            localisation=serializer.validated_data['localisation'],
            description_experience=serializer.validated_data['description_experience'],
            image_url=serializer.validated_data.get('image_url'),
            about_me = serializer.validated_data.get('about_me'),
            birth_date = serializer.validated_data.get('birth_date'),
            postal_code = serializer.validated_data.get('postal_code'),

        )
        
        metiers_data = serializer.validated_data['metiers']
        professional.metiers.set(metiers_data)  # Set the many-to-many relationship
        professional.save()

        return Response({'message': 'Professional request submitted, awaiting approval'})
    
    return Response(serializer.errors, status=400)


#for admin panel (can accept or reject)
@api_view(['GET'])
@permission_classes([IsAdminUser])  # Only admins can access
def list_pending_professionals(request):
    pending_professionals = Professional.objects.filter(status='en attente')
    serializer = ProfessionalSerializer(pending_professionals, many=True)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def update_professional_status(request, pk):
    try:
        professional = Professional.objects.get(pk=pk, status='en attente')
    except Professional.DoesNotExist:
        return Response({'error': 'Professional not found or already reviewed'}, status=404)
    
    serializer = ProfessionalStatusUpdateSerializer(professional, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': f'Professional status updated to {serializer.validated_data["status"]}'})
    return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([AllowAny])  # Ensure only authenticated users can access
def list_professionals(request):
    """
    Retrieve all professionals' information, including their average review (avis_moyenne).
    """
    professionals = Professional.objects.all()  # Fetch all professionals from the database
    serializer = ProfessionalSerializer(professionals, many=True)  # Serialize the queryset
    return Response(serializer.data)  # Return serialized data in the response

@api_view(['GET'])
@permission_classes([AllowAny])  # Ensure only authenticated users can access
def get_professional_detail(request, pk):
    """
    Retrieve detailed information about a specific professional by their ID.
    """
    try:
        professional = Professional.objects.get(pk=pk)  
    except Professional.DoesNotExist:
        return Response({'error': 'Professional not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProfessionalSerializer(professional)  
    return Response(serializer.data)  


# Vue pour récupérer les clients
@api_view(['GET'])
@permission_classes([IsAdminUser]) 
def list_clients(request):
    clients = Client.objects.all()
    serializer = ClientSerializer(clients, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_metiers(request):
    metiers = Metier.objects.all()
    serializer = MetierSerializer(metiers, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_metier_detail(request, pk):

    try:
        metier = Metier.objects.get(pk=pk)  
    except Metier.DoesNotExist:
        return Response({'error': 'metier not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = MetierSerializer(metier)  
    return Response(serializer.data)  

# View to create a new review
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_avis_view(request, prof_id):
    try:
        professional = Professional.objects.get(id=prof_id)
    except Professional.DoesNotExist:
        return Response({'error': 'Professional not found'}, status=404)

    if AvisProf.objects.filter(professionnel=professional, client=request.user.client).exists():
        return Response({'error': 'You have already reviewed this professional'}, status=400)
    print(professional)
    print(request.user.client)

    serializer = AvisProfSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(client=request.user.client, professionnel=professional)
        return Response(serializer.data, status=201)
    
    return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_avis_view(request, prof_id):
    try:
        professional = Professional.objects.get(id=prof_id)
    except Professional.DoesNotExist:
        return Response({'error': 'Professional not found'}, status=404)

    reviews = AvisProf.objects.filter(professionnel=professional).order_by('-date_avis')
    serializer = AvisProfSerializer(reviews, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Ensuring the user is authenticated
def list_notifications_view(request):
    notifications = Notification.objects.filter(id_receveur=request.user.client).order_by('-date_recoi')
    print(notifications)
    # Serialize the notifications
    serializer = NotificationSerializer(notifications, many=True)

    # Return the serialized data
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])  # Ensure that the user is authenticated
def create_notification_view(request):
    if 'contenu' not in request.data or 'id_receveur' not in request.data:
        return Response({'error': 'contenu and id_receveur are required.'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = NotificationSerializer(data=request.data)
    if serializer.is_valid():
        notification = serializer.save(id_receveur_id=request.data['id_receveur'])
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_annonce_view(request):
    """Create a new annonce."""
    serializer = AnnonceSerializer(data=request.data)
    if serializer.is_valid():
        # Ensure the logged-in user is a professional
        try:
            professional = request.user.client.professional
        except Professional.DoesNotExist:
            return Response({'error': 'You must be a professional to create an annonce.'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save(professionnel=professional)  
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_annonces_view(request,id_prof):
    try:
        prof = Professional.objects.get(id=id_prof)
    except Professional.DoesNotExist:
            return Response({'error': 'This pk Professional does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        
    annonces = Annonce.objects.filter(professionnel=prof).order_by('-date_publication')  
    serializer = AnnonceSerializer(annonces, many=True)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_annonce_view(request, annonce_id):

    try:
        annonce = Annonce.objects.get(id_annonce=annonce_id)
    except Annonce.DoesNotExist:
        return Response({'error': 'Annonce not found.'}, status=status.HTTP_404_NOT_FOUND)


    if annonce.professionnel.client != request.user.client:
        return Response({'error': 'You can only delete your own annonces.'}, status=status.HTTP_403_FORBIDDEN)
    
    annonce.delete()
    return Response({'message': 'Annonce deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
