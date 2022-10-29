from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.http import JsonResponse

from auctions.listingSerializer import listingSerializer
from .models import *
import pusher
import json

pusher_client = pusher.Pusher(app_id=u'1491853', key=u'9a86192d4367cb474002', secret=u'1300125c70764c3dc3e7', cluster=u'ap2')


def index(request):
    return render(request, "auctions/index.html", {
        "active_listings": Listing.objects.filter(active=True)
    })


def new_listing(request):
    if request.method == 'GET':
        return render(request, "auctions/newlisting.html")
    else:
        new_listing = Listing(
            owner=request.user,
            title=request.POST["title"],
            description=request.POST["description"],
            current_price=int(request.POST["starting_bid"]),
            category=request.POST["category"],
            image_url=request.POST["image_url"],
            active=True,
            winner=request.user)

         
        new_listing.save()
        serializer = listingSerializer(new_listing)
        pusher_client.trigger('cache-listing', 'listing-updated', serializer.data)   
        return HttpResponseRedirect(reverse("index"))


def listing(request, title):
    if request.method == 'GET':
        listing = Listing.objects.get(title=title)
        min_bid = int(Listing.objects.get(title=title).current_price +1)
        if request.user.is_authenticated:
            in_watchlist = listing in (request.user).watchlist.all()
        else:
            in_watchlist = False
        is_winner = (request.user == listing.winner) and (listing.active == False)
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "min_bid": min_bid,
            "comments": listing.listing_comments.all(),
            "in_watchlist": in_watchlist,
            "is_owner": request.user == listing.owner,
            "is_winner": is_winner
            })
    elif "bid_form" in request.POST:
        listing = Listing.objects.get(title=title)
        for bid in listing.bids_made.all():
            bid.delete()
        new_bid = Bid(
            bid_to=listing, bid_value=int(request.POST["bid"]), bidder=request.user)
        new_bid.save()
        listing.current_price = new_bid.bid_value
        listing.winner = request.user
        listing.save()
        serializer = listingSerializer(listing)
        pusher_client.trigger('cache-listing', 'listing-updated', serializer.data)  
        min_bid = int(listing.current_price +1)
        return HttpResponseRedirect(reverse("listing", args=(title,)))
    elif "comment_form" in request.POST:
        listing = Listing.objects.get(title=title)
        new_comment = Comment(
            comment=request.POST["comment"],
            commented_to=listing, commented_by=request.user)
        new_comment.save()
        min_bid = int(listing.current_price +1)
        return HttpResponseRedirect(reverse("listing", args=(title,)))
    elif "watchlist_add_button" in request.POST:
        watchlist = (request.user).watchlist
        requested_listing = Listing.objects.get(title=title)
        # if requested_listing not in watchlist:
        watchlist.add(requested_listing)
        return HttpResponseRedirect(reverse("listing", args=(title,)))
    elif "watchlist_remove_button" in request.POST:
        watchlist = (request.user).watchlist
        requested_listing = Listing.objects.get(title=title)
        watchlist.remove(Listing.objects.get(title=title))
        return HttpResponseRedirect(reverse("listing", args=(title,)))
    elif "close_listing_button" in request.POST:
        listing = Listing.objects.get(title=title)
        listing.active = False
        listing.save()
        serializer = listingSerializer(listing)
        pusher_client.trigger('cache-listing', 'listing-updated', serializer.data)
        return HttpResponseRedirect(reverse("listing", args=(title,)))


def categories(request):
    listings = Listing.objects.all()
    listing_categories = (listing.category for listing in listings)
    listing_categories = list(set(listing_categories))
    #extract all the categories and make a set to prevent duplicates
    listing_categories.sort()
    return render(request, "auctions/categories.html", {
        "listing_categories": listing_categories
    })


def category(request, category):
    listings = Listing.objects.filter(category=category, active=True)
    #we can use index.html with a variable only containing a spesific category
    return render(request, "auctions/index.html", {
        "active_listings": listings
    })


def watchlist(request, username):
    if request.method == "GET":
        return render(request, "auctions/watchlist.html", {
            "watchlist": (User.objects.get(username=username)).watchlist.all()
        })


def auctionswon(request, username):
    if request.method == "GET":
        return render(request, "auctions/auctionswon.html", {
            "auctionswon": (User.objects.get(username=username)).won_listings.all()
        })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
