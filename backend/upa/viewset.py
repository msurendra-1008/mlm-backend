from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from .models import UPARegistration
from .serializers import UPAUserSerializer

class UPAUserViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing UPAUser instances.
    """
    queryset = UPARegistration.objects.all()
    serializer_class = UPAUserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated] 

    @action(detail=False, methods=['post'], url_path='upa_registration')
    def upa_registration(self, request):
        """
        Custom API for UPA Registration.
        This method handles user registration under a parent user with a reference_id.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        upa_user = serializer.save()
        
        # Perform the registration
        # self.perform_create(serializer)
        
        return Response({
            'message': 'Registration successful!',
            'upa_user': UPAUserSerializer(upa_user).data
        }, status=status.HTTP_201_CREATED)
