import asyncio
import datetime
import random
import string
import time
from typing import List
from rest_framework_simplejwt.tokens import RefreshToken

from authapp.models import AuthTempCode, User
from authapp.serializer import JWTTokenSerializer
from authapp.services.login.exceptions import TempCodeDoesNotExist, TempCodeExpired, \
    TempCodeMaxRetryAttempts, WrongTempCode
from config import settings


class LoginService():

    def send_code(self, phone: str) -> str:
        code = self._generate_code(letters=string.digits, length=4)
        user = self._get_or_create_user_by_phone(phone)
        self._create_or_update_temp_code(user, code)

        # sending code
        self._send_code(phone, code)

        return code

    def login(self, phone: str, code: str) -> JWTTokenSerializer:
        user = self._get_or_create_user_by_phone(phone)

        self._check_temp_code(user, code)
        self._activate_user(user)

        refresh = RefreshToken.for_user(user)  # type: ignore
        return JWTTokenSerializer({
            "access": str(refresh.access_token),  # type: ignore
            "refresh": str(refresh),
        })

    def _activate_user(self, user: User):
        user.is_active = True
        user.save(update_fields=["is_active"])

    def _get_or_create_user_by_phone(self, phone: str) -> User:
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            referral_code = self._generate_referral_code()
            user = User.objects.create_user(    # type: ignore
                phone=phone, referral_code=referral_code)

        return user

    def _create_or_update_temp_code(self, user: User, code: str):
        try:
            auth_code = AuthTempCode.objects.get(user=user)
            auth_code.temp_code = code
            auth_code.save(update_fields=["temp_code"])
        except AuthTempCode.DoesNotExist:
            AuthTempCode.objects.create(user=user, temp_code=code)

    def _check_temp_code(self, user: User, code: str):
        try:
            auth_code = AuthTempCode.objects.get(user=user)
        except AuthTempCode.DoesNotExist:
            raise TempCodeDoesNotExist()

        if (auth_code.created_at + settings.AUTH_TEMP_CODE_LIFETIME).timestamp() < datetime.datetime.now().timestamp():
            auth_code.delete()
            raise TempCodeExpired()

        if (auth_code.temp_code != code):
            auth_code.retry_attempts += 1
            if auth_code.retry_attempts >= settings.AUTH_TEMP_CODE_MAX_RETRY_ATTEMPTS:
                auth_code.delete()
                raise TempCodeMaxRetryAttempts()

            auth_code.save(update_fields=["retry_attempts"])
            raise WrongTempCode()

        auth_code.delete()

    def _send_code(self, phone: str, code: str):
        print("\n\n\n", code, "\n\n\n")
        time.sleep(1)

    def _generate_referral_code(self) -> str:
        while True:
            letters = string.ascii_uppercase + string.digits
            code = self._generate_code(letters=letters, length=6)
            try:
                User.objects.get(referral_code=code)
            except User.DoesNotExist:
                return code

    def _generate_code(self, letters: str, length: int) -> str:
        rand_string = ''.join(random.choice(letters) for i in range(length))
        return rand_string
