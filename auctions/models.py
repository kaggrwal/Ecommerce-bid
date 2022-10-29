from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    watchlist = models.ManyToManyField(
        'Listing', blank=True, related_name="watching_users")


class Listing(models.Model):
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="my_listings")
    title = models.CharField(max_length=32)
    description = models.CharField(max_length=128)
    current_price = models.IntegerField()
    category = models.CharField(max_length=16)
    image_url = models.CharField(max_length=1000)
    active = models.BooleanField(default=True)
    winner = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="won_listings")


class Bid(models.Model):
    bid_to = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="bids_made")
    bid_value = models.IntegerField()
    bidder = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bids")


class Comment(models.Model):
    comment = models.CharField(max_length=64)
    commented_to = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="listing_comments")
    commented_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_comments")
