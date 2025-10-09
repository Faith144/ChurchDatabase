from django.shortcuts import render

from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from core.models import Sermon
from .serializers import SermonSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """
    User registration endpoint
    """
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    # Validation
    if not username or not password or not email:
        return Response(
            {'error': 'Username, email and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {'error': 'Email already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Create token
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'message': 'User created successfully'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """
    User login endpoint
    """
    from django.contrib.auth import authenticate
    
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)
    
    if user:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'email': user.email
        })
    else:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
def logout_user(request):
    """
    User logout endpoint
    """
    # Delete the token to log out
    if hasattr(request.user, 'auth_token'):
        request.user.auth_token.delete()
    
    return Response({'message': 'Successfully logged out'})




class SermonViewSet(viewsets.ModelViewSet):
    queryset = Sermon.objects.all().select_related('assembly')
    serializer_class = SermonSerializer
    permission_classes = [IsAuthenticated]  # Require authentication for all actions
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['assembly', 'preacher', 'sermon_date']
    search_fields = ['title', 'preacher', 'bible_passage', 'notes']
    ordering_fields = ['sermon_date', 'created_at', 'title']
    ordering = ['-sermon_date']
    
    # Optional: Allow read-only access for unauthenticated users
    # permission_classes = [IsAuthenticatedOrReadOnly]
    
    def perform_create(self, serializer):
        # You can add custom logic here, like setting the user who created the sermon
        serializer.save()
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def public(self, request):
        """Public endpoint that doesn't require authentication"""
        recent_sermons = Sermon.objects.all().order_by('-sermon_date')[:5]
        serializer = self.get_serializer(recent_sermons, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Protected endpoint - requires authentication"""
        recent_sermons = Sermon.objects.all().order_by('-sermon_date')[:10]
        serializer = self.get_serializer(recent_sermons, many=True)
        return Response(serializer.data)