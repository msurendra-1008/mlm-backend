from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, LegIncomeModel, IncomeSetting, IncomeSettingForWomenOld

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = CustomUser
        fields = ('mobile', 'name', 'email', 'password')
        # extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            name = validated_data['name'],
            mobile = validated_data['mobile'],
            password = validated_data['password']
        )
        
        return user
    
    
class UserLoginSerializer(serializers.ModelSerializer):
    mobile = serializers.CharField()
    password = serializers.CharField(write_only=True)
    name = serializers.CharField(read_only=True)
    token = serializers.CharField(read_only=True)
    
    class Meta:
        model = CustomUser
        fields = ('mobile', 'name', 'email', 'password', 'token')
    
    def validate(self, data):
        mobile = data.get('mobile')
        password = data.get('password')
        
        if mobile and password:
            user = authenticate(mobile=mobile, password=password)
            if user is None:
                raise serializers.ValidationError('Invalid Credentials')
        else:
            raise serializers.ValidationError('both "mobile" and "password" are required')

        data['user'] = user
        return data
    

class LegIncomeModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegIncomeModel
        fields = ['id', 'leg1', 'leg2', 'leg3', 'income']
        
        


# General Income setting serializer 

class IncomeSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeSetting
        fields = '__all__'

class IncomeSettingForWomenOldSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeSettingForWomenOld
        fields = '__all__'
        
        
#  show user list with their associated leg user data.
class LegUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'uid_no', 'name', 'mobile')

class CustomUserTreeSerializer(serializers.ModelSerializer):
    left_leg = LegUserSerializer()
    middle_leg = LegUserSerializer()
    right_leg = LegUserSerializer()

    class Meta:
        model = CustomUser
        fields = ('id', 'uid_no', 'name', 'mobile', 'left_leg', 'middle_leg', 'right_leg')