from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser

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