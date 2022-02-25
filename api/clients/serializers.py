from django.contrib.auth.hashers import make_password

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from .models import Client, Match


class ClientSerializer(serializers.ModelSerializer):
    is_match = serializers.SerializerMethodField()
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(
            queryset=Client.objects.all()
        )]
    )

    class Meta:
        fields = [
            'id', 'username', 'email', 'first_name', 'password',
            'last_name', 'avatar', 'gender', 'is_match',
            'longitude', 'latitude'
        ]
        extra_kwargs = {'password': {'write_only': True}}
        model = Client

    def get_is_match(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        if obj.is_followed:
            return True
        return False

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super(ClientSerializer, self).create(validated_data)


class ClientMatchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Match
        fields = [
            'follower', 'person'
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=Match.objects.all(),
                fields=['follower', 'person'],
                message=('Вы уже отметили этого человека.')
            )
        ]

    def validate(self, data):
        person = data.get('person')
        follower = self.context['request'].user
        if follower == person:
            message = 'Вы не можете отметить себя самого.'
            raise serializers.ValidationError(message)
        return data
