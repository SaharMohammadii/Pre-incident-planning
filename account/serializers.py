from rest_framework import serializers
from .models import OTP, User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from djoser.serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView


class AuthenticatedTokenVerifyView(TokenVerifyView):
    permission_classes = [IsAuthenticated, ]


class AuthenticatedTokenRefreshView(TokenRefreshView):
    permission_classes = [IsAuthenticated, ]


class PhoneSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)



class OTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp_code = serializers.CharField()


class AccountUserSerializer(UserSerializer):

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'personnel_code',
            'staff_status',
        )

    def to_representation(self, instance):
        user =  super().to_representation(instance)

        return user




class UserTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # jwt info
        token['user_id'] = user.id        
        token['user_role'] = user.user_role
        token['name'] = user.first_name + " " + user.last_name


        return token