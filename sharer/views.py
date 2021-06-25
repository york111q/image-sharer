from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render

from rest_framework import generics, mixins, status
from rest_framework.authentication import (TokenAuthentication,
                                           SessionAuthentication)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserImage, ImageURL, codemaker
from .permissions import ExpiryLinksPermission
from .serializers import (UserImageSerializer, LoginSerializer,
                          ImageURLSerializer)

from datetime import timedelta, datetime


# Create your views here.

class APIOverview(APIView):

    def get(self, request):
        links = {
                 '/login/': 'Login page',
                 '/logout/': 'Logout page',
                 '/images/': 'List of all images and upload image',
                 '/images/code': 'Detail view of image/thumbnail and'
                                 'expiry link creation'
        }

        return Response({'Available links:': links})


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def get(self, request):
        return Response({'Please log in'})

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(username=serializer.validated_data["username"],
                                password=serializer.validated_data["password"])
            if user is not None:
                login(request, user)
                return Response(status=status.HTTP_202_ACCEPTED)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'Error': 'Serializer is not valid'})


class LogoutView(APIView):
    def get(self, request, format=None):
        logout(request)
        return Response(status=status.HTTP_200_OK)


class UserImageView(generics.GenericAPIView, mixins.CreateModelMixin):
    serializer_class = UserImageSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserImage.objects.filter(user=self.request.user)

    def get(self, request):
        urls = [img.get_urls() for img in self.get_queryset()]
        return Response(urls)

    def post(self, request):
        return self.create(request)

    def perform_create(self, serializer):
        serializer.validated_data['user'] = self.request.user
        serializer.save()


class DetailImageView(generics.GenericAPIView):
    serializer_class = ImageURLSerializer
    queryset = ImageURL.objects.all()
    permission_classes = [ExpiryLinksPermission]

    def get_object(self, code):
        try:
            return ImageURL.objects.get(code=code)
        except ImageURL.DoesNotExist:
            return False

    def get(self, request, code):
        thumb = self.get_object(code)

        if thumb:
            if thumb.expiry_date:
                if thumb.expiry_date.replace(tzinfo=None) < datetime.now():
                    thumb.delete()
                    return Response(status=status.HTTP_404_NOT_FOUND)
            return Response(thumb.thumb.url)

        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request, code):
        serializer = ImageURLSerializer(data=request.data)
        serializer.validate(request.data)

        expiry_sec = int(request.data['expire_after_seconds'])
        expiry_date = datetime.now() + timedelta(seconds=expiry_sec)

        img_url = ImageURL.objects.get(code=code)
        img, created = ImageURL.objects.update_or_create(image=img_url.image,
                                                         type=img_url.type,
                                                         expiry_date=expiry_date,
                                                         defaults={'thumb': img_url.thumb})
        if created:
            img.code=codemaker()
            img.save()

        user_info = {
                     'Created url': '/images/' + img.code,
                     'Expire': img.expiry_date.strftime("%m/%d/%Y, %H:%M:%S")
        }

        return Response(user_info, status=status.HTTP_202_ACCEPTED)
