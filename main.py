# For API calls
import requests

# For parsing API JSON object responses
import json

# For printing to an excel sheet
import csv

# For extracting raw HTML from a website
import urllib

# For getting the current date to better organize data
from datetime import datetime as date

# For cleaning the HTML and extracting body text
from bs4 import BeautifulSoup as bSoup

# For extracting relevant information from the data
from pyspark.sql import SparkSession

# site = 'https://stackoverflow.com/questions/28610508/how-to-get-raw-html-text-of-a-given-url-using-python'
# htmlSite = urllib.request.urlopen(site)
# soup = bSoup(htmlSite, 'html.parser')
# print(soup)

#Purpose: Get all steam reviews for the dataset of game titles we give to the function
#Input: some dataset with the steam games we want analyzed
#Result: reviewList now filled with all reviews for their corresponding game titles
#Returns: None
def getAllGameReviews(dataset):
    #Steam API parameters for what we want: all recent reviews(including positive and negative) in English in the last 10 days, purchased from anywhere
    #More info here: https://partner.steamgames.com/doc/store/getreviews
    parameters = {'filter': 'recent', 'language': 'english', 'day_range': '10', 'start_offset': '0',
                  'review_type': 'all',
                  'purchase_type': 'all'}
    #Go through all games in the database
    for i in range(len(appNameAndID["applist"]["apps"])):
        # Reset offset to 0 after every game
        parameters["start_offset"] = 0
        # Get a new game to analyze
        response = requests.get(
            'https://store.steampowered.com/appreviews/' + str(appNameAndID["applist"]["apps"][i]["appid"]) + '?json=1',
            params=parameters,timeout=300)
        reviewsResponse = response.json()
        # If the query is empty, skip that game/app
        if reviewsResponse["success"] == 2:
            continue
        print("Looking through reviews for game: " + str(appNameAndID["applist"]["apps"][i]["name"]))
        #print("_____________________________THE FOLLOWING IS FOR THE GAME: " + str(dataset["games"][i]["title"]))
        # Go through all the reviews for a given game
        for j in range(0, reviewsResponse["query_summary"]["total_reviews"], 20):
            # Go through all reviews for the game in batches of 20
            # Place them in the proper location in our reviewList dataset based on the game
            for k in range(len(reviewsResponse["reviews"])):
                #debugging statement to check if we are really getting reviews
                #print(reviewsResponse["reviews"][k]["review"])
                reviewList["titles"][appNameAndID["applist"]["apps"][i]["name"]]["reviews"].append({
                    reviewsResponse["reviews"][k]["review"]
                })
                print(reviewsResponse["reviews"][k]["review"])
            # Get the next batch of 20, e.g. first we get reviews 0-20, then 21-40, etc..
            parameters["start_offset"] += 20
            response = requests.get(
                'https://store.steampowered.com/appreviews/' + str(appNameAndID["applist"]["apps"][i]["appid"]) + '?json=1',
                params=parameters,timeout=300)
            reviewsResponse = response.json()
        print("@@@@@@@@@@@Done looking through reviews for game: " + str(appNameAndID["applist"]["apps"][i]["name"]) + "@@@@@@@@@@@")
#Get a list of all games on Steam
response = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2/")
appNameAndID = response.json()

#key: game name, value: game's app id, e.g. dataset["Counter-Strike"] returns 10 (its appid)
dataset = {}
#key: "titles"->game name->reviews, value: all reviews for that game in an arbitrary order
reviewList = {
    'titles': {
    }
}

#Populate our dataset with all available apps/games on Steam
for i in range(len(appNameAndID["applist"]["apps"])):
    dataset.update({
        appNameAndID["applist"]["apps"][i]["name"] : appNameAndID["applist"]["apps"][i]["appid"]
    })
    reviewList["titles"].update({
        appNameAndID["applist"]["apps"][i]["name"] : {
            'reviews' : [
            ]
        }
    })

#Get all game reviews for all games in our dataset
getAllGameReviews(dataset)

#with open('data.csv', 'a', newline='', encoding='utf-8') as f:
#    w = csv.writer(f)
#    w.writerows("a")
#    w.writerows("b")