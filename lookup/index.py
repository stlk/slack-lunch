import os
import requests
import logging
import datetime
from flask import jsonify, request
from app_generator import create_app


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
    logging.info(f"looking for " + restaurant["restaurant"]["name"])
    menu = None
    try:
        menu = zomato_api_call(
            f"https://developers.zomato.com/api/v2.1/dailymenu?res_id={restaurant_id}"
        )
    except:
        logging.exception("Daily menu request failed")

    if menu and menu["daily_menus"]:
        menu_data = menu["daily_menus"][0]["daily_menu"]
        restaurant_name = restaurant["restaurant"]["name"]
        menu_date = datetime.datetime.strptime(
            menu_data["start_date"], "%Y-%m-%d %H:%M:%S"
        ).strftime("%A, %d. %B")
        dishes = "\n".join([format_dish(dish) for dish in menu_data["dishes"]])
        return f"*{restaurant_name}*\n{menu_date}\n\n{dishes}"


def get_restaurants(location, lat, lng, response_url):
    restaurants = zomato_api_call(
        f"https://developers.zomato.com/api/v2.1/search?lat={lat}&lon={lng}&radius=500&sort=real_distance"
    )

    daily_menus = [
        try_get_daily_menu(restaurant) for restaurant in restaurants["restaurants"]
    ]

    text = "\n\n".join([menu for menu in daily_menus if menu])
    text = text or "Nothing found :space_invader:"
    response = requests.post(
        response_url, json={"response_type": "in_channel", "text": text, "mrkdwn": True}
    )
    logging.info(response)


app = create_app()


@app.route("/lookup", methods=["POST"])
def rate():
    location = request.json["location"]
    lat = request.json["lat"]
    lng = request.json["lng"]
    response_url = request.json["response_url"]

    get_restaurants(location, lat, lng, response_url)

    return f"OK"
