import urllib
import requests
from django.contrib.auth import get_user_model, login
from django.core import signing
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView
from django.shortcuts import redirect, render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.conf import settings
from urllib.parse import urlencode

from config import settings
from django.urls import reverse

from users.models import Users
from users.serializers import NicknameSerializer

NAVER_CALLBACK_URL = 'oauth/naver/callback'
NAVER_STATE = 'naver_login'
NAVER_LOGIN_URL = 'https://nid.naver.com/oauth2.0/authorize'
NAVER_TOKEN_URL = 'https://nid.naver.com/oauth2.0/token'
NAVER_PROFILE_URL = 'https://openapi.naver.com/v1/nid/me'
User = get_user_model()


class NaverLoginRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        domain = self.request.scheme + '://' + self.request.META.get('HTTP_HOST', '127.0.0.1:8000')
        callback_url = domain + NAVER_CALLBACK_URL
        state = signing.dumps(NAVER_STATE)

        params = {
            'response_type': 'code',
            'client_id': settings.NAVER_CLIENT_ID,
            'redirect_uri': callback_url,
            'state': state
        }

        return f'{NAVER_LOGIN_URL}?{urlencode(params)}'


def naver_callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')

    if NAVER_STATE != signing.loads(state):
        raise Http404('Invalid state')

    access_token = get_naver_access_token(code, state)

    profile_response = get_naver_profile(access_token)
    email = profile_response.get('email')
    user = User.objects.filter(email=email).first()

    if user:
        if not user.is_active:
            user.is_active = True
            user.save()

        login(request, user)
        return redirect(reverse("account-list-create"))
    nickname_url = reverse("oauth:nickname")
    if not user:
        user = User.objects.create_user(
            email=email,
            password='temp_password',  # 임시 비밀번호
            phone_number='some_phone_number'  # 적절한 값으로 수정
        )
    return redirect(f'{nickname_url}?access_token={access_token}')


@csrf_exempt
@api_view(['GET'])
def oauth_nickname(request):
    access_token = request.GET.get('access_token')

    if not access_token:
        return Response({'error': 'No access token provided'}, status=status.HTTP_400_BAD_REQUEST)

    data = {'nickname': request.GET.get('nickname')}
    serializer = NicknameSerializer(data=data)
    if serializer.is_valid():
        profile = get_naver_profile(access_token)
        email = profile.get('email')

        if Users.objects.filter(email=email).exists():
            return Response({'error': 'Email already registered'}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save(
            email=email,
            name=profile.get('name', ''),
            phone_number=profile.get('mobile', ''),
            is_active=True
        )

        login(request, user)
        return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_naver_access_token(code, state):
    params = {
        'grant_type': 'authorization_code',
        'client_id': settings.NAVER_CLIENT_ID,
        'client_secret': settings.NAVER_SECRET,
        'code': code,
        'state': state
    }

    response = requests.get(NAVER_TOKEN_URL, params=params)
    result = response.json()
    return result.get('access_token')


def get_naver_profile(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(NAVER_PROFILE_URL, headers=headers)
    if response.status_code != 200:
        raise Http404('Invalid Access Token')

    return response.json().get('response')
