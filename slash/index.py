import os
import logging
import requests
from flask import request
from app_generator import create_app

opencagedata_api_key = os.environ.get("OPENCAGEDATA_API_KEY")


def geocode(location):
    response = requests.get(
        f"https://api.opencagedata.com/geocode/v1/json?q={location}&key={opencagedata_api_key}&pretty=1"
    )
    result = response.json()["results"][0]
    return (result["formatted"], result["geometry"]["lat"], result["geometry"]["lng"])


app = create_app()


@app.route("/slash", methods=["POST"])
def rate():
    query = request.form["text"]
    response_url = request.form["response_url"]
    location, lat, lng = geocode(query)

    logging.info(f"query: {query}, location: {location}")

    try:
        requests.post(
            "https://slack-food.stlk.now.sh/lookup",
            json={
                "location": location,
                "lat": lat,
                "lng": lng,
                "response_url": response_url,
            },
            timeout=(1, 0.01),
        )
    except:
        logging.exception("lookup request")

    return f"Looking for restaurants in {location}"
