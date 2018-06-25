#For API calls
import requests

#For parsing API JSON object responses
import json

#For printing to an excel sheet
import csv

#For extracting raw HTML from a website
import urllib

#For getting the current date to better organize data
from datetime import datetime as date

#For cleaning the HTML and extracting body text
from bs4 import BeautifulSoup as bSoup

#For extracting relevant information from the data
from pyspark.sql import SparkSession

#site = 'https://stackoverflow.com/questions/28610508/how-to-get-raw-html-text-of-a-given-url-using-python'
#htmlSite = urllib.request.urlopen(site)
#soup = bSoup(htmlSite, 'html.parser')
#print(soup)

response = requests.get("https://api.steampowered.com/ISteamApps/GetAppList/v2/")
data = response.json()
#iterates over whole JSON object
i = 0
for _ in range(len(data["applist"]["apps"])):
    print("Game: ", data["applist"]["apps"][i]["name"], "has appid: ", data["applist"]["apps"][i]["appid"])
    i += 1