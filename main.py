# For API calls
import requests

# For parsing API JSON object responses
import json

# For data handling
import pandas as pd

# For extracting raw HTML from a website
import urllib

# For getting the current date to better organize data
from datetime import datetime as date

# For cleaning the HTML and extracting body text
from bs4 import BeautifulSoup as bSoup

# For extracting relevant information from the data
from pyspark.sql import SparkSession

# For data management
import sqlite3

connection = sqlite3.connect("data.db")
crsr = connection.cursor()
crsr.execute('''CREATE TABLE reviews (
review_id INTEGER PRIMARY KEY,
game_name TEXT,
review TEXT,
time_created INTEGER)''')

#Get a list of all games on Steam
response = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2/")
appNameAndID = response.json()
#key: game name, value: game's app id, e.g. dataset["Counter-Strike"] returns 10 (its appid)
gameIDMapping = {}
#key: "titles"->game name->reviews, value: all reviews for that game in an arbitrary order
reviewList = {
    'titles': {
    }
}
#Populate our dataset with all available apps/games on Steam
for i in range(len(appNameAndID["applist"]["apps"])):
    gameIDMapping.update({
        appNameAndID["applist"]["apps"][i]["name"] : appNameAndID["applist"]["apps"][i]["appid"]
    })
    reviewList["titles"].update({
        appNameAndID["applist"]["apps"][i]["name"] : {
            'reviews' : [
            ]#,
            #'dates' : [
            #]
        }
    })

# Get all game reviews for all games in our dataset
# Steam API parameters for what we want: all recent reviews(including positive and negative) in English in the last 10 days, purchased from anywhere
# More info here: https://partner.steamgames.com/doc/store/getreviews
parameters = {'filter': 'recent', 'language': 'english', 'day_range': '10', 'start_offset': '0',
              'review_type': 'all',
              'purchase_type': 'all',
              'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
# Go through all games in the database
for app in appNameAndID["applist"]["apps"]:
    # Reset offset to 0 after every game
    parameters["start_offset"] = 0
    # Get a new game to analyze
    try:
        response = requests.get(
            'https://store.steampowered.com/appreviews/' + str(app["appid"]) + '?json=1',
            params=parameters, timeout=5)
    except requests.exceptions.RequestException as e:
        print(e)
    reviewsResponse = response.json()
    # If the query is empty, skip that game/app
    if reviewsResponse["success"] == 2:
        continue
    if reviewsResponse["query_summary"]["total_reviews"] == 0:
        continue
    # print("_____________________________THE FOLLOWING IS FOR THE GAME: " + str(dataset["games"][i]["title"]))
    # Go through all the reviews for a given game
    for j in range(0, reviewsResponse["query_summary"]["total_reviews"], 20):
        # Go through all reviews for the game in batches of 20
        # Place them in the proper location in our reviewList dataset based on the game
        for review in reviewsResponse["reviews"]:
            reviewList["titles"][app["name"]]["reviews"].append({
                review["review"]
            })
            crsr.execute("INSERT OR REPLACE INTO reviews VALUES (NULL, ?, ?, ?)", (app["name"], review["review"], review["timestamp_created"]))
            connection.commit()
        # Get the next batch of 20, e.g. first we get reviews 0-20, then 21-40, etc..
        parameters["start_offset"] += 20
        try:
            response = requests.get(
                'https://store.steampowered.com/appreviews/' + str(
                    app["appid"]) + '?json=1',
                params=parameters, timeout=5)
        except requests.exceptions.RequestException as e:
            print(e)
            continue
        reviewsResponse = response.json()
        print(str(j) + " reviews done for game " + app["name"])
connection.close()