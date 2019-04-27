import logging
import os
import pprint
import requests
import datetime
import background
from logging.handlers import SysLogHandler
from typing import NamedTuple
from flask import Flask, Response, __version__, jsonify, request
from request_logger import attach_logger

opencagedata_api_key = os.environ.get("OPENCAGEDATA_API_KEY")


def geocode(location):
    response = requests.get(
        f"https://api.opencagedata.com/geocode/v1/json?q={location}&key={opencagedata_api_key}&pretty=1"
    )
    result = response.json()["results"][0]
    return (result["formatted"], result["geometry"]["lat"], result["geometry"]["lng"])


def zomato_api_call(path):
    header = {
        "Accept": "application/json",
        "user_key": os.environ.get("ZOMATO_API_KEY"),
    }
    response = requests.get(path, headers=header)
    response.raise_for_status()
    return response.json()


def format_dish(dish):
    dish_price = dish["dish"]["price"]
    if dish_price:
        dish_price = f"*{dish_price}*"
    return dish["dish"]["name"] + " " + dish_price


def try_get_daily_menu(restaurant):
    restaurant_id = restaurant["restaurant"]["id"]
    print(f"looking for " + restaurant["restaurant"]["name"])
    try:
        menu = zomato_api_call(
            f"https://developers.zomato.com/api/v2.1/dailymenu?res_id={restaurant_id}"
        )
        if menu["daily_menus"]:
            menu_data = menu["daily_menus"][0]["daily_menu"]
            restaurant_name = restaurant["restaurant"]["name"]
            menu_date = datetime.datetime.fromisoformat(
                menu_data["start_date"]
            ).strftime("%A, %d. %B")
            dishes = "\n".join([format_dish(dish) for dish in menu_data["dishes"]])
            return f"*{restaurant_name}*\n{menu_date}\n\n{dishes}"
    except Exception as error:
        print(error)


@background.task
def get_restaurants(location, lat, lng, response_url):
    restaurants = zomato_api_call(
        f"https://developers.zomato.com/api/v2.1/search?lat={lat}&lon={lng}&radius=500&sort=real_distance"
    )

    daily_menus = [
        try_get_daily_menu(restaurant) for restaurant in restaurants["restaurants"]
    ]

    text = "\n\n".join([menu for menu in daily_menus if menu])
    text = text or "Nothing found"
    response = requests.post(
        response_url, json={"response_type": "in_channel", "text": text, "mrkdwn": True}
    )
    print(response)


def create_app(config=None):
    app = Flask(__name__)

    app.config.update(config or {})

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    attach_logger(app)

    @app.route("/")
    def index():
        return jsonify({"test": "hi"})

    @app.route("/slash", methods=["POST"])
    def rate():
        query = request.form["text"]
        location, lat, lng = geocode(query)
        print(f"query: {query}")
        print(f"location: {location}")
        get_restaurants(location, lat, lng, request.form["response_url"])

        return f"Looking for restaurants in {location}"

    return app
