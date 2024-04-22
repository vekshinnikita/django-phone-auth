

import re
import string
from typing import Union
from authapp.models import User
from authapp.services.referral.exceptions import ReferralAlreadyApplied, ReferralCodeDoesNotExist


class ReferralService:

    def set_invited_user(self, user: User, referral_code: str):
        if user.invited_user is not None:
            raise ReferralAlreadyApplied()

        user.invited_user = self._get_user_by_invited_code(  # type: ignore
            referral_code)
        user.save(update_fields=['invited_user'])

    def check_referral_code(self, code: Union[str, None]) -> Union[str, None]:
        if code is None:
            return "Required field"

        code = code.upper()

        letters = string.ascii_uppercase + string.digits
        pattern = r'[' + letters + r']{6}'

        match = re.fullmatch(pattern, code)

        if len(code) != 6:
            return "The code must contain 6 characters"

        if not match:
            return "The code must contain only numbers and Latin letters"

        return None

    def _get_user_by_invited_code(self, code: str) -> User:
        try:
            user = User.objects.get(referral_code=code)
        except User.DoesNotExist:
            raise ReferralCodeDoesNotExist()

        return user
