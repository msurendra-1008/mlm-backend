
from accounts.models import CustomUser
from .models import UPARegistration
from rest_framework import serializers


class UPAUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UPARegistration
        fields = ['address', 'state', 'city', 'pincode', 'reference_id']

    def validate(self, attrs):
        reference_id = attrs.get('reference_id')
        
        # Find the parent user by reference_id
        try:
            parent_user = CustomUser.objects.get(uid_no=reference_id)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("No user found with the provided reference UID.")
        
        # Check if the referenced user already has all legs assigned
        if parent_user.left_leg and parent_user.middle_leg and parent_user.right_leg:
            raise serializers.ValidationError("The referenced user already has all legs assigned.")
        
        return attrs

    def create(self, validated_data):
        reference_id = validated_data.get('reference_id')
        user = self.context['request'].user  # Assuming the user is obtained from the request context
        
        # Find the parent user by reference_id
        try:
            parent_user = CustomUser.objects.get(uid_no=reference_id)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("No user found with the provided reference UID.")
        
        # Check if the current user is the one being referenced
        # if user != parent_user:
        #     raise serializers.ValidationError("The current user does not match the reference UID.")
        
        # Assign the current user to an available leg of the parent user
        if not parent_user.left_leg:
            parent_user.left_leg = user
        elif not parent_user.middle_leg:
            parent_user.middle_leg = user
        elif not parent_user.right_leg:
            parent_user.right_leg = user
        else:
            raise serializers.ValidationError("All legs are already filled. Cannot assign the new user.")
        
        # Save the updated parent user
        parent_user.save()

        # Create and return the UPAUser instance
        upa_user = UPARegistration.objects.create(**validated_data)
        return upa_user