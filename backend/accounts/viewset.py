from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from .models import ( CustomUser, 
                     LegIncomeModel, 
                     IncomeSetting, 
                     IncomeSettingForWomenOld, 
                     DoubleIncomeSettingForBPLHandicap
)
from .serializers import (
     UserRegistrationSerializer, 
     UserLoginSerializer, 
     LegIncomeModelSerializer, 
     IncomeSettingSerializer, 
     IncomeSettingForWomenOldSerializer, 
     CustomUserTreeSerializer, 
     DoubleIncomeSettingForBPLHandicapSerializer
)
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
    
    
    
    
# General Income Setting:
class GeneralIncomePagination(PageNumberPagination):
    page_size = 10
class IncomeSettingViewSet(viewsets.ModelViewSet):
    queryset = IncomeSetting.objects.all().order_by('created_date')
    serializer_class = IncomeSettingSerializer
    pagination_class = GeneralIncomePagination

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_income = instance.income

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        new_income = serializer.validated_data.get('income', old_income)

        # If income is being changed, set previous_income to old_income
        if new_income != old_income:
            serializer.save(previous_income=old_income)
        else:
            serializer.save()

        return Response(serializer.data)
    

class IncomeSettingForWomenOldViewSet(viewsets.ModelViewSet):
    queryset = IncomeSettingForWomenOld.objects.all().order_by('created_date')
    serializer_class = IncomeSettingForWomenOldSerializer
    pagination_class = GeneralIncomePagination

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_income = instance.income

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        new_income = serializer.validated_data.get('income', old_income)

        # If income is being changed, set previous_income_for_women_old to old_income
        if new_income != old_income:
            serializer.save(previous_income_for_women_old=old_income)
        else:
            serializer.save()

        return Response(serializer.data)
    

class IncomeSettingForBPLHandicapViewSet(viewsets.ModelViewSet):
    queryset = DoubleIncomeSettingForBPLHandicap.objects.all().order_by('created_date')
    serializer_class = DoubleIncomeSettingForBPLHandicapSerializer
    pagination_class = GeneralIncomePagination

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_income = instance.income

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        new_income = serializer.validated_data.get('income', old_income)

        # If income is being changed, set previous_income to old_income
        if new_income != old_income:
            serializer.save(previous_income=old_income)
        else:
            serializer.save()

        return Response(serializer.data)
    
class CustomUserTreeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserTreeSerializer