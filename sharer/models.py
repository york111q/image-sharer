from django.conf import settings
from django.contrib.auth.models import (AbstractUser, AbstractBaseUser,
                                        BaseUserManager)
from django.core.files import File
from django.core.validators import FileExtensionValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.authtoken.models import Token

import os, random, string
from io import BytesIO
from PIL import Image


THUMB_DIR = os.path.join('sharer', 'thumbnails')
THUMB_TYPES = (('small', 'small'),
               ('large', 'large'),
               ('original', 'original'))


def get_upload_path(userimage, filename):
    return os.path.join('sharer', str(userimage.user.username), str(filename))


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


# Create your models here.
class AccountTier(models.Model):
    name = models.CharField(max_length=32)

    small_thumb_allow = models.BooleanField(default=True)
    small_thumb_height = models.IntegerField(default=200)

    large_thumb_allow = models.BooleanField(default=False)
    large_thumb_height = models.IntegerField(default=400)

    original_img_allow = models.BooleanField(default=False)

    expiring_link_allow = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class MyUserManager(BaseUserManager):

    def create_user(self, username, password=None):
        if not username:
            raise ValueError("You need to have username")

        user = self.model(username=username)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, password=None):
        user = self.create_user(username=username, password=password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class MyUser(AbstractBaseUser, BaseUserManager):
    username = models.CharField(max_length=32, unique=True)
    date_joined = models.DateTimeField(verbose_name='date joined',
                                       auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    account_type = models.ForeignKey(AccountTier, on_delete=models.SET_NULL,
                                     null=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = MyUserManager()

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


class ImageURL(models.Model):
    image = models.ForeignKey('UserImage', on_delete=models.CASCADE)
    type = models.CharField(max_length=16, choices=THUMB_TYPES)
    thumb = models.ImageField(upload_to=THUMB_DIR)
    code = models.CharField(max_length=16, unique=True, null=True)
    expiry_date = models.DateTimeField(null=True)


def codemaker():
    length = 10
    while True:
        code = ''.join(random.choices(string.ascii_lowercase, k=length))
        if ImageURL.objects.filter(code=code).count() == 0:
            return code


def make_thumbnail(image, height, type):
    im = Image.open(image)
    im.convert('RGBA')
    im.thumbnail((height, height))
    thumb_io = BytesIO()
    im.save(thumb_io, 'PNG', quality=85)
    thumbnail = File(thumb_io, name=image.name)
    orig_img = UserImage.objects.get(image=image)
    img, created = ImageURL.objects.update_or_create(image=orig_img,
                                                     type=type,
                                                     defaults={'thumb': thumbnail})
    if created:
        img.code=codemaker()
        img.save()

    return img.code


class UserImage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_upload_path,
                              validators=[FileExtensionValidator(['jpg', 'png'])])

    def get_urls(self):
        acc_type = self.user.account_type

        if not acc_type:
            return Response({"You don't have valid account type, please contact"
                             "admin to get account type"},
                             status=status.HTTP_403_FORBIDDEN)

        urls = [{'Image': self.image.url}]

        if acc_type.small_thumb_allow:
            height = acc_type.small_thumb_height
            code = make_thumbnail(self.image, height, 'small')
            urls.append({'Small thumbnail url': '/images/' + code,
                         'Small thumbnail max size': f'{height}px'})

        if acc_type.large_thumb_allow:
            height = acc_type.large_thumb_height
            code = make_thumbnail(self.image, height, 'large')
            urls.append({'Large thumbnail url': '/images/' + code,
                         'Large thumbnail max size': f'{height}px'})

        if acc_type.original_img_allow:
            height = 99999 # Assuming noone will add larger picture
            img, created = ImageURL.objects.update_or_create(image=self,
                                                             type='original',
                                                             defaults={'thumb': self.image})
            if created:
                img.code=codemaker()
                img.save()
            urls.append({'Original image url': '/images/' + img.code})

        return urls
