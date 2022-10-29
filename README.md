# Ecommerce-Bid

## An online ecommerce store to auction different items and users can bid on them. This uses [pusher](https://pusher.com/) to implement the live count of bidding users on the particular item and the lates bid of the items.

Screenshot of the website in action:

[![image.png](https://i.postimg.cc/nVN7GyBj/Screenshot-from-2022-10-29-22-39-31.png)](https://postimg.cc/BtcXqwh4)

## Setup

1. Install the [pipenv](https://pypi.org/project/pipenv/)

Clone this repo and run:

```bash
    pipenv install
    pipenv run python3 manage.py migrate
    pipenv run python3 manage.py runserver
```