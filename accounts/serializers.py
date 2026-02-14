from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Membership

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    membership_type = serializers.ChoiceField(
        choices=Membership.MEMBERSHIP_CHOICES,
        write_only=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'membership_type']

    def create(self, validated_data):
        membership_type = validated_data.pop('membership_type')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        # Set cashback based on membership type
        if membership_type == "STUDENT":
            cashback = 10.00
        else:
            cashback = 2.00

        Membership.objects.create(
            user=user,
            membership_type=membership_type,
            cashback_percentage=cashback,
            is_student_verified=False
        )

        return user
