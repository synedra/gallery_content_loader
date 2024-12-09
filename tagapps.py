from __future__ import print_function
from dotenv import load_dotenv
from astrapy import DataAPIClient

from github import Github

import os.path
import os
import json
import re
import frontmatter 

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")


my_client = DataAPIClient(token)
my_database = my_client.get_database_by_api_endpoint(
    "https://3c18f9b2-3f49-4e7b-8cd4-f238b06dbca5-us-east-2.apps.astra.datastax.com",
    keyspace="gallery",
)

app_collection = my_database.create_collection("examples_and_starters", check_exists= False)

# using an access token
f = open("github.token", "r")
line = f.readlines()[0].replace("\n", "")
g = Github(line)

p = re.compile('[a-zA-Z]+')


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    print("Starting")
    entries = []
    
    counter = 0
    github = {}
    counter = 0

    quickstarts = []
    quickstart_content = []
   
    # Just for fun, get all the repos for Datastax-Examples
    repo = g.get_repo("synedra/fusionauth-site")
    
    quickstarts_list = repo.get_contents("astro/src/content/quickstarts")

    for index in range(len(quickstarts_list)):
        if "quickstart-" in quickstarts_list[index].path:
            quickstarts.append(quickstarts_list[index].path)

    for quickstart in quickstarts:
        qs = repo.get_contents(quickstart).decoded_content.decode() 
        fm = frontmatter.loads(qs)
        qs_info = {"tags": []}
        if "title" not in fm:
            continue
        if ("title" in fm and fm["title"] == ""):
            continue
        
        for variable in ("title","icon","description","prerequisites","navcategory",
                            "section","technology","language","faIcon","color","codeRoot"):
            if variable in ("description", "prerequisites", "title"):
                qs_info[variable] = fm[variable] if variable in fm else ""
            elif variable in ("section","technology","language","navcategory") and variable in fm:
                lowervalue = fm[variable].lower()
                if lowervalue not in qs_info["tags"]:
                    qs_info["tags"].append(lowervalue) 
                qs_info[variable] = lowervalue if variable in fm else ""
            else:
                qs_info[variable] = fm[variable].lower() if variable in fm else ""
            
            qs_info["_id"] = qs_info["title"].lower()
        try:
            postdoc=qs_info
            print ("Inserting app " + qs_info["title"] + " now")
            res = app_collection.replace_one(
                replacement=postdoc,filter={'_id':qs_info["_id"]},upsert=True)

        except Exception as ex:
                print("ERROR")
                print(ex)
                print("NERROR")

    # Example applications
    examples = repo.get_contents("/astro/src/content/json/exampleapps.json").decoded_content.decode() 
    qs = json.loads(examples)
    # Load the json into an object in python


    for example in qs:
        if example["name"] == "":
            continue
        if "quickstart" in example["tags"]:
            continue
        if "tags" in example:
            qs_info = {"tags":example["tags"]}
        else:
            qs_info = {"tags":[]}
        
        qs_info["title"] = example["name"]
        qs_info["language"] = example["language"].lower()
        qs_info["tags"].append(example["language"].lower())
        qs_info["description"] = example["description"]
        qs_info["codeRoot"] = example["url"]
        if "icon" in example:
            qs_info["icon"] = example["icon"]
        else:
            qs_info["icon"] = "/img/icons/security.svg",
        
        qs_info["_id"] = qs_info["title"].lower()
        try:
            postdoc=qs_info
            print ("Inserting app " + qs_info["title"] + " now")
            res = app_collection.replace_one(
                replacement=postdoc,filter={'_id':qs_info["_id"]},upsert=True)

        except Exception as ex:
                print("ERROR")
                print(ex)
                print("NERROR")


if __name__ == '__main__':
    main()
