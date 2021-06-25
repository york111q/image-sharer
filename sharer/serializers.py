from rest_framework import serializers

from .models import UserImage, MyUser, ImageURL


class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserImage
        fields = ('image', )


class ImageURLSerializer(serializers.ModelSerializer):
    expire_after_seconds = serializers.IntegerField()

    class Meta:
        model = ImageURL
        fields = ('expire_after_seconds', )

    def validate(self, data):
        expire = int(data['expire_after_seconds'])
        if expire < 300 or expire > 30000:
            raise serializers.ValidationError("Number of seconds should be in"
                                              "range: 300-30000")
        return data


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=32, required=True)
    password = serializers.CharField(write_only=True, required=True,
                                     max_length=32)
