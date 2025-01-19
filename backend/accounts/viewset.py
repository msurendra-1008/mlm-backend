from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from .models import CustomUser, LegIncomeModel
from .serializers import UserRegistrationSerializer, UserLoginSerializer, LegIncomeModelSerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny



class PublicViewSet(viewsets.ViewSet):
    authentication_classes = [TokenAuthentication]
    # permission_classes = [AllowAny]
    @action(detail=False, methods=['get'], url_path='status')
    def status(self, request):
        return Response({
            'message': 'API is working fine!'
        })


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegistrationSerializer

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'name': user.name,
            'mobile': user.mobile,
            'upa_uid_number': user.uid_no,
            'account_balance': user.account_balance,
            'message': "Logged in successfully!"
        }, status=status.HTTP_200_OK) 
    


class LegIncomeModelViewSet(viewsets.ModelViewSet):
    queryset = LegIncomeModel.objects.all()
    serializer_class = LegIncomeModelSerializer