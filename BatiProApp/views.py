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

        # Set the password correctly before saving the user


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

    # Validate the request data with the serializer
    serializer = ProfessionalRequestSerializer(data=request.data)
    if serializer.is_valid():
        # Create a professional instance linked to the current user
        client = request.user.client
        professional = Professional.objects.create(
            client = client ,  # Link the professional to the current user
            localisation=serializer.validated_data['localisation'],
            description_experience=serializer.validated_data['description_experience'],
            image_url=serializer.validated_data.get('image_url'),

        )
        
        # Set the metiers (many-to-many relationship)
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



# @api_view(['GET'])
def home(request):
    metier1 = Metier.objects.all()
    metier_ser = MetrierSerializer(metier1 , many=True)
    reported_data = {
        'data': metier_ser.data
    }
    commande = Commande.objects.get(id=1)
    livraison = Livraison.objects.get(id=1)


    print(f"Le Total de Commande: {commande.total()}\nle Frais de livraison:{livraison.frais_livraison}\nLe Total delivraison: {livraison.total()}\n")
    # return Response(reported_data, status=status.HTTP_200_OK)
    return render(request,'BatiProApp/home.html',{'m':metier_ser.data})

from BatiProApp.models import Professional 
def dele(request):
 # Adjust the import according to your app name and model location
    Professional.objects.all().delete()
    print("All Professional records deleted successfully.")




