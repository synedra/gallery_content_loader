from __future__ import print_function
from dotenv import load_dotenv
from astrapy.db import AstraDB, AstraDBCollection
import astrapy

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

my_client = astrapy.DataAPIClient()
my_database = my_client.get_database(
    api_endpoint,
    token=token,
)

tag_collection = ""

tag_collection = my_database.create_collection("tag_collection2", check_exists= False)

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
        try:
            qs = repo.get_contents(quickstart).decoded_content.decode() 
            fm = frontmatter.loads(qs)
            qs_info = {"tags":[]}
            for variable in ("title","icon","description","prerequisites","navcategory",
                             "section","technology","language","faIcon","color","codeRoot","navcategory"):
                if variable in ("description", "prerequisites"):
                    qs_info[variable] = fm[variable] if variable in fm else ""
                else:
                    qs_info[variable] = fm[variable].lower() if variable in fm else ""
                if variable in ("section","technology","language","navcategory") and variable in fm:
                    qs_info["tags"].append(fm[variable].lower()) 
                    qs_info[variable] = fm[variable].lower() if variable in fm else ""
                qs_info["_id"] = qs_info["title"]
                quickstart_content.append(qs_info)
            
        except:
            raise ValueError()
                
    uniquelinks = []

    tagdict = {}
    tagdict["all"] = {}
    tagdict["all"]["apps"] = []
    tagtype = {"all":""}

    for entry in quickstart_content:
        print(entry)
        print ("\n\n")
        if "tags" in entry:
            for tag in entry["tags"]:
                
                if tag.lower() not in tagdict.keys():
                    tagdict[tag.lower()] = {
                        "name": tag.lower(), "apps": [entry]}
                else:
                    if entry not in tagdict[tag.lower()]["apps"]:
                        tagdict[tag.lower()]["apps"].append(entry)

    names = []
    tagdict["all"]["apps"] = []

    # Remove dupes in all
    for tag in tagdict.keys():
        for app in tagdict[tag]["apps"]:
            if app["title"] not in names:
                tagdict["all"]["apps"].append(app)
                names.append(app["title"])
            
    print (tagdict.keys())

    for tag in tagdict.keys():
        count = len(tagdict[tag]["apps"])
        tagdict[tag]["count"] = count
        

        try:
            postdoc={"_id": tag, "title": tag.lower(), "count": count, "apps": tagdict[tag.lower()]["apps"], "tagtype":tagtype[tag.lower()]}
            print ("Inserting tag " + tag + " now")
            print (postdoc)
            res = tag_collection.insert_one(
                document=postdoc)
            
        except Exception as ex:
            print("ERROR")
            print(ex)



if __name__ == '__main__':
    main()
