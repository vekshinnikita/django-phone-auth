from rest_framework import serializers

from .models import User


class UserReferralSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'phone',
            'firstname',
            'lastname',
            'patronymic',
            'referral_code',
        )


class UserSerializer(serializers.ModelSerializer):

    referrals = serializers.SerializerMethodField('get_referrals')

    def get_referrals(self, instance: User):
        refs = User.objects.filter(invited_user=instance)
        serializer = UserReferralSerializer(refs, many=True)
        return serializer.data

    class Meta:
        model = User
        fields = (
            'id',
            'phone',
            'firstname',
            'lastname',
            'patronymic',
            'referral_code',
            'referrals',
        )


class JWTTokenSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class UserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'firstname',
            'lastname',
            'patronymic',
        )
