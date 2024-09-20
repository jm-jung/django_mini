from django.urls import path
from . import oauth_views

app_name = 'oauth'
urlpatterns = [
    path('login/', oauth_views.NaverLoginRedirectView.as_view(), name='naver_login'),
    path('callback/', oauth_views.naver_callback, name='naver_callback'),
]
