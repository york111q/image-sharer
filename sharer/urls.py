from django.urls import path

from rest_framework.authtoken.views import obtain_auth_token

from . import views

urlpatterns = [
    path('', views.APIOverview.as_view(), name='overview'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('images/', views.UserImageView.as_view(), name='images'),
    path('images/<str:code>', views.DetailImageView.as_view(), name='detail')
]
