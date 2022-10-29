from rest_framework import serializers
from auctions.models import Listing

class listingSerializer(serializers.Serializer):

      owner = serializers.CharField(required = False)
      title = serializers.CharField(read_only = True)
      description = serializers.CharField(read_only = True)
      current_price = serializers.IntegerField(read_only = True)
      category = serializers.CharField(read_only = True)
      image_url = serializers.CharField(read_only = True)
      winner = serializers.CharField(read_only = True)
      active = serializers.BooleanField(read_only = True)


def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return Listing.objects.create(**validated_data)

def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.owner = validated_data.get('owner', instance.owner)
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.current_price = validated_data.get('current_price', instance.current_price)
        instance.category = validated_data.get('category', instance.category)
        instance.image_url = validated_data.get('image_url', instance.image_url)
        instance.winner = validated_data.get('winner', instance.winner)
        instance.active = validated_data.get('active', instance.active)

        instance.save()
        return instance


