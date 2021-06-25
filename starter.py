import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imgsharer.settings')
import django
django.setup()

from sharer.models import AccountTier

AccountTier.objects.get_or_create(name="Basic")
AccountTier.objects.get_or_create(name="Premium", large_thumb_allow=True, original_img_allow=True)
AccountTier.objects.get_or_create(name="Enterprise", large_thumb_allow=True, original_img_allow=True, expiring_link_allow=True)
