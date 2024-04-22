from os import access
from django.http import HttpRequest
from rest_framework.response import Response
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status, generics, permissions


from authapp.models import User
from authapp.serializer import JWTTokenSerializer, UserSerializer, UserUpdateSerializer
from authapp.services.login.service import LoginService
from authapp.services.login.exceptions import TempCodeDoesNotExist, TempCodeExpired, \
    TempCodeMaxRetryAttempts, WrongTempCode
from authapp.services.referral.service import ReferralService
from authapp.services.referral.exceptions import ReferralAlreadyApplied, ReferralCodeDoesNotExist

# Create your views here.


class AuthByPhoneView(APIView):
    serializer_class = JWTTokenSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request: HttpRequest):
        phone = request.POST.get('phone', None)
        code = request.POST.get('code', None)

        if not phone:
            return Response({
                'phone': "Required field"
            }, status=status.HTTP_400_BAD_REQUEST)

        login_service = LoginService()
        if not code:
            return Response({
                'code': "Required field"
            }, status=status.HTTP_400_BAD_REQUEST)

        if not code.isdigit():
            return Response({
                'code': "Must be an int"
            }, status=status.HTTP_400_BAD_REQUEST)

        code = code

        err_message = None
        try:
            token_serializer = login_service.login(phone, code)
        except WrongTempCode:
            err_message = 'Wrong temp code'
        except TempCodeDoesNotExist:
            err_message = "You need to request one-time code"
        except TempCodeMaxRetryAttempts:
            err_message = 'The maximum number of retries has been reached'
        except TempCodeExpired:
            err_message = 'Сode has expired, request it again'

        if err_message is not None:
            return Response({'message': err_message},
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(token_serializer.data, status=status.HTTP_200_OK)


class RequestAuthCodeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request: HttpRequest):
        phone = request.POST.get('phone', None)

        if not phone:
            return Response({
                'phone': "Required field"
            }, status=status.HTTP_400_BAD_REQUEST)

        login_service = LoginService()
        code = login_service.send_code(phone)

        return Response({
            'code': code,
            'message': "Code has been sent to the phone number"
        }, status=status.HTTP_200_OK)


class GetMeView(generics.GenericAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return User.objects \
            .filter(id=self.request.user.id).first()  # type: ignore

    def get(self, request: HttpRequest):
        query = self.get_queryset()
        return Response(
            UserSerializer(query).data,
            status=status.HTTP_200_OK
        )


class UpdateUserView(generics.UpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()

    def patch(self, request, *args, **kwargs):
        self.kwargs['pk'] = request.user.id
        return super().patch(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        self.kwargs['pk'] = request.user.id
        return super().put(request, *args, **kwargs)


class ApplyInvitedUser(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        referral_code = request.POST.get('referral_code', None)
        referral_service = ReferralService()

        ref_err_message = referral_service.check_referral_code(referral_code)

        if (ref_err_message):
            return Response({
                'referral_code': ref_err_message
            }, status=status.HTTP_400_BAD_REQUEST)

        err_message = None
        try:
            referral_service.set_invited_user(request.user, referral_code)
        except ReferralAlreadyApplied:
            err_message = "The code has already been applied"
        except ReferralCodeDoesNotExist:
            err_message = "The referral code does not exist"

        if err_message:
            return Response({
                'message': err_message
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)
