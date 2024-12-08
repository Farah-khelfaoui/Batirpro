from django.shortcuts import render,HttpResponse
from .models import *
from rest_framework import generics , status
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated , AllowAny, IsAdminUser
from rest_framework.authtoken.models import Token 
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .serializers import *
from django.db.models import Q

def process_request(request):
    print("Incoming Request:")
    print(f"Method: {request.method}")
    print(f"Path: {request.path}")
    print(f"Headers: {request.headers}")
    print(f"Body: {request.body}")

@api_view(['POST'])
@permission_classes([AllowAny]) 
def register_view(request):
    print(request.body)
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



# linked with the front
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    process_request(request)
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({'message': 'Login successful', 'token': token.key})
    else:
        return Response({'error': 'User name or password incorrect. Please try again'}, status=401)

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

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_professional_profile_view(request):
    try:
        professional = request.user.client.professional
    except Professional.DoesNotExist:
        return Response({'error': 'You are not registered as a professional.'}, status=status.HTTP_404_NOT_FOUND)
    serializer = ProfessionalUpdateSerializer(professional, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()  
        return Response({'message': 'Profile updated successfully.'})
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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


from django.db.models import  Case, When, IntegerField

@api_view(['GET'])
@permission_classes([AllowAny])
def search_professionals(request):
    nom = request.GET.get('nom', '').strip()
    localisation = request.GET.get('localisation', '').strip()
    metiers_ids = request.GET.getlist('metiers')  
        
    metiers = [int(m_id) for m_id in metiers_ids if m_id.isdigit()]

    professionals = Professional.objects.all()
    
    query = Q()

    if nom:
        query |= Q(client__first_name__icontains=nom) | Q(client__last_name__icontains=nom)
    
    if localisation:
        query |= Q(localisation__icontains=localisation)
    
    if metiers_ids:
        query |= Q(metiers__id_metier__in=metiers)

    professionals = professionals.filter(query).distinct()

    professionals = professionals.annotate(
        match_score=(
            Case(
                When(client__first_name__icontains=nom, then=1),
                When(client__last_name__icontains=nom, then=1),
                default=0,
                output_field=IntegerField()
            ) +
            Case(
                When(localisation__icontains=localisation, then=1),
                default=0,
                output_field=IntegerField()
            ) +
            Case(
                When(metiers__id_metier__in=metiers, then=1),
                default=0,
                output_field=IntegerField()
            )
        )
    )

    professionals = professionals.order_by('-match_score') 

    serializer = ProfessionalSerializer(professionals, many=True)
    return Response(serializer.data)


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
@permission_classes([IsAuthenticated]) 
def list_notifications_view(request):
    notifications = Notification.objects.filter(id_receveur=request.user.client).order_by('-date_recoi')
    print(notifications)
    # Serialize the notifications
    serializer = NotificationSerializer(notifications, many=True)

    # Return the serialized data
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])  
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_marketowner(request):
    try:
        client = Client.objects.get(user_ptr=request.user)  # Ensure the client exists
    except Client.DoesNotExist:
        return Response({'error': 'User must be registered as a client first.'}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = MarketownerSerializer(data=request.data)
    if serializer.is_valid():

        marketowner = Marketowner.objects.create(
            client=client,
            adresse=serializer.validated_data['adresse'],
            current_marketplace=serializer.validated_data.get('current_marketplace')
        )
        
        return Response({'message': 'Marketowner request submitted, awaiting approval.'}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_market_member(request):
    try:
        client = Client.objects.get(user_ptr=request.user)
    except Client.DoesNotExist :
        return Response({'error': 'User must be registered as a client first.'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = MarketMemberSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Market member created successfully.'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_marketplace(request):
    try:
        client = Client.objects.get(user_ptr=request.user)
    except Client.DoesNotExist:
        return Response({'error': 'User must be registered as a client first.'}, status=status.HTTP_400_BAD_REQUEST)

    if MarketMember.objects.filter(client=client).exists():
        return Response({'error': 'User is already a market member.'}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = MarketplaceSerializer(data=request.data)
    if serializer.is_valid():
        marketplace = serializer.save(status='pending')
        market_member = MarketMember.objects.create(client=client , current_marketplace = marketplace )
        marketplace.members.add(market_member)  
        
        return Response({'message': 'Marketplace created successfully and pending approval.'}, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_pending_marketplaces(request):
    pending_marketplaces = Marketplace.objects.filter(status='pending')
    serializer = MarketplaceSerializer(pending_marketplaces, many=True)
    return Response(serializer.data)

@api_view(['PATCH','POST'])
@permission_classes([IsAdminUser])  
def update_marketplace_status(request, pk):
    try:
        marketplace = Marketplace.objects.get(pk=pk)
    except Marketplace.DoesNotExist:
        return Response({'error': 'Marketplace not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    new_status = request.data.get('status')
    if new_status not in ['accepted', 'rejected','pending']:
        return Response({'error': 'Invalid status. Use "accepted" or "rejected" or "pending".'}, status=status.HTTP_400_BAD_REQUEST)
    
    marketplace.status = new_status
    marketplace.save()
    return Response({'message': f'Marketplace status updated to {new_status}.'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_market_member(request, marketplace_id):
    try:
        marketplace = Marketplace.objects.get(id_marketplace=marketplace_id)
    except Marketplace.DoesNotExist:
        return Response({'error': 'Marketplace not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    client = request.user.client
    if not marketplace.members.filter(client=client).exists():
        return Response({'error': 'You are not authorized to add members to this marketplace.'}, status=status.HTTP_403_FORBIDDEN)

    new_client_id = request.data.get('client_id')
    try:
        new_client = Client.objects.get(pk=new_client_id)
    except Client.DoesNotExist:
        return Response({'error': 'Client not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    new_member, created = MarketMember.objects.get_or_create(client=new_client, current_marketplace=marketplace.id_marketplace)
    marketplace.members.add(new_member)
    
    return Response({'message': 'Market member added successfully.'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([AllowAny])
def MarketPlaces(request):
        marketplaces = Marketplace.objects.prefetch_related('categories', 'avis').all()
        serializer = MarketplaceSerializer(marketplaces, many=True)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def MarketplaceDetail(request, pk):
    marketplace = get_object_or_404(Marketplace, pk=pk)

    marketplace_serializer = MarketplaceSerializer(marketplace)

    annonces = AnnonceMarket.objects.filter(marketplace=marketplace)
    annonces_serializer = AnnonceSerializer(annonces, many=True)
    
    categories = marketplace.categories.all()  
    categories_serializer = CategorieSerializer(categories, many=True)

    avis = AvisMarket.objects.filter(marketplace=marketplace)
    avis_serializer = AvisMarketSerializer(avis, many=True)
    

    data = marketplace_serializer.data
    data['annonces'] = annonces_serializer.data
    data['categories'] = categories_serializer.data
    data['avis'] = avis_serializer.data
    
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_avis(request, marketplace_id):
    try:
        marketplace = Marketplace.objects.get(pk=marketplace_id)
    except Marketplace.DoesNotExist:
        return Response({'error': 'Marketplace not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if AvisMarket.objects.filter(marketplace=marketplace, client=request.user.client).exists():
        return Response({'error': 'You have already reviewed this marketplace.'}, status=status.HTTP_400_BAD_REQUEST)
    
    data = {
        'marketplace': marketplace_id,
        'client': request.user.client.id,  
        'note': request.data.get('note'),
        'commentaire': request.data.get('commentaire')
    }
    serializer = AvisMarketSerializer(data=data)
    
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_annonce(request, marketplace_id):
    try:
        marketplace = Marketplace.objects.get(pk=marketplace_id)
    except Marketplace.DoesNotExist:
        return Response({'error': 'Marketplace not found'}, status=status.HTTP_404_NOT_FOUND)

    if not marketplace.members.filter(client=request.user.client).exists():
        return Response({'error': 'You are not a member of this marketplace.'}, status=status.HTTP_403_FORBIDDEN)
    
    data = {
        'titre': request.data.get('titre'),
        'contenu': request.data.get('contenu'),
        'image_url': request.data.get('image_url'),
        'marketplace': marketplace_id
    }
    serializer = AnnonceMarketSerializer(data=data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_product(request):
    member = get_object_or_404(MarketMember, client=request.user)
    marketplace = member.current_marketplace  
    
    data = request.data.copy()
    data['marketplace'] = marketplace.id_marketplace
    
    serializer = ProduitSerializer(data=data)
    if serializer.is_valid():
        serializer.save(marketplace=marketplace)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_product(request, pk):
    member = get_object_or_404(MarketMember, client=request.user)
    product = get_object_or_404(Produit, pk=pk, marketplace=member.current_marketplace)
    
    serializer = ProduitSerializer(product, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_product(request, pk):
    member = get_object_or_404(MarketMember, client=request.user)
    product = get_object_or_404(Produit, pk=pk, marketplace=member.current_marketplace)
    product.delete()
    return Response({'message': 'Produit supprimé avec succès'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_products(request):
    produits = Produit.objects.all()
    serializer = ProduitSerializer(produits, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_product_review(request, produit_id):
    produit = get_object_or_404(Produit, pk=produit_id)

    if AvisProduit.objects.filter(produit=produit, client=request.user.client).exists():
        return Response({'error': 'You have already reviewed this product.'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = AvisProduitSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(produit=produit, client=request.user.client)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([AllowAny])
def search_products(request):
    nom = request.GET.get('nom', '').strip()
    categorie_id = request.GET.get('categorie', '').strip()
    materiaux = request.GET.get('materiaux', '').strip()
    sort_by = request.GET.get('sort_by', '').strip()  

    produits = Produit.objects.all()

    query = Q()
    if nom:
        query |= Q(nom__icontains=nom)
    if categorie_id and categorie_id.isdigit():
        query |= Q(categorie__id=categorie_id)
    if materiaux:
        query |= Q(materiaux__icontains=materiaux)

    produits = produits.filter(query).distinct()


    produits = produits.annotate(average_note=Avg('avis__note'))
    print(produits)

    if sort_by == 'prix':
        produits = produits.order_by('prix')  
    elif sort_by == 'note':
        produits = produits.order_by('-average_note')  

    serializer = ProduitSerializer(produits, many=True)
    return Response(serializer.data)




# marketplace
# products

@api_view(['GET'])
@permission_classes([AllowAny])
def list_products_home(request):
    produits = Produit.objects.all()[:4]
    product_serializer = ProduitSerializer(produits, many=True)
    professionals = Professional.objects.all()[:4]  # Fetch all professionals from the database
    prof_serializer = ProfessionalSerializer(professionals, many=True)  # Serialize the queryset
    response_data = {
        'products': product_serializer.data,
        'professionals': prof_serializer.data
    }
    return Response(response_data)


@api_view(['GET'])
@permission_classes([AllowAny])  # Ensure only authenticated users can access
def list_professionals_home(request):
    professionals = Professional.objects.all()[:4]  # Fetch all professionals from the database
    serializer = ProfessionalSerializer(professionals, many=True)  # Serialize the queryset
    return Response(serializer.data)  # Return serialized data in the response
