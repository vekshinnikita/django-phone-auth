from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from authapp.views import AuthByPhoneView, RequestAuthCodeView, GetMeView, ApplyInvitedUser, UpdateUserView

urlpatterns = [
    path('request_code/', RequestAuthCodeView.as_view()),
    path('login/', AuthByPhoneView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('me/', GetMeView.as_view()),
    path('me/update/', UpdateUserView.as_view()),
    path('ref_code/apply/', ApplyInvitedUser.as_view()),
]
