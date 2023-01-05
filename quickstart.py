from __future__ import print_function
from github import Github

import os.path
import os
import json
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from astrapy.client import create_astra_client

from astrapy.client import create_astra_client

astra_client = create_astra_client(astra_database_id=os.environ["ASTRA_DB_ID"],
                                   astra_database_region=os.environ["ASTRA_DB_REGION"],
                                   astra_application_token=os.environ["ASTRA_DB_APPLICATION_TOKEN"])
my_collection = astra_client.collections.namespace("test").collection("apps1227a")
tag_collection = astra_client.collections.namespace("test").collection("tags1227a")
# using an access token
f = open("github.token","r")
line = f.readlines()[0].replace("\n","")
g = Github(line)

p = re.compile('[a-zA-Z]+')

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '1vJSKJAa7EJ0s1Ksn_L_lgQGJI6-UMDqNngrQO4U4cEY'
SAMPLE_RANGE_NAME = 'SampleApplicationMain'


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    entries = []
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()
    
    # Call the Sheets API for SampleApplication links
    result = service.spreadsheets().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,ranges=SAMPLE_RANGE_NAME,fields="sheets/data/rowData/values/hyperlink,sheets/data/rowData/values/textFormatRuns/format/link/uri").execute()
    values = result.get('sheets', [])

    sampleApplicationLinks = values[0]["data"][0]["rowData"]

    # Call the Sheets API for SampleApplication items
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    sampleApplicationItems = result.get('values', [])

    # Workshop sheet for links
    WORKSHOP_SAMPLE_RANGE_NAME = 'WorkshopCatalog'

    # Call the Sheets API for Workshop Links
    result = service.spreadsheets().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,ranges=WORKSHOP_SAMPLE_RANGE_NAME,fields="sheets/data/rowData/values/hyperlink,sheets/data/rowData/values/textFormatRuns/format/link/uri").execute()
    values = result.get('sheets', [])
    workshopLinks = values[0]["data"][0]["rowData"]
        
    # Get the items for Workshops
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=WORKSHOP_SAMPLE_RANGE_NAME).execute()
    workshopItems = result.get('values', [])
    
    counter = 0
    for entry in sampleApplicationItems:
        urls={}
        if counter==0:
            counter += 1
            continue

        counter += 1
        summary = ""
        if '\n' in entry[0]:
            (name, summary) = entry[0].split('\n')
        else:
            if entry[0] == "":
                continue
            name = entry[0]
        
        badge = entry[1]

        links = sampleApplicationLinks
        if (len(links) > counter-1 and "values" in links[counter-1]):
            urlcheck = links[counter-1]["values"]
            getLinks(urlcheck, urls)
        
        tags = []
        language = []
       #Language
        if (entry[2] != [""]):
            language = entry[2].replace(" ","\n").replace("\n",",").split(",")
            for item in language:
                if (p.match(item) and item.lower() not in tags):
                    tags.append(item.lower())

        #Stack should be an array
        if (entry[3] != [""]):
            stack = entry[3].replace(" ","\n").replace("\n", ",").split(",")
            for item in stack:  
                if ((p.match(item)) and item.lower() not in tags):
                    tags.append(item.lower())

        # APIs
        entrynumber = 6
        apiarray = []
        for api in [ "DATA", "DOC", "GQL", "CQL", "GRPC", "DB", "IAM", "STRM" ]:
            if entry[entrynumber] == 'TRUE':
                apiarray.append(api)
                tags.append(api + " API")
            entrynumber += 1

        newtags = []

        for tag in tags:
            if not (p.match(tag)):
                continue
            newtags.append(tag)

        new_item = {
            "name":name,
            "summary":summary,
            "urls":urls,
            "language":language,  
            "stack":stack,
            "usecases": entry[4],
            "owner":entry[5],
            "apis":apiarray,
            "tags":newtags
        }

        entries.append(new_item)
        
    counter = 0

    for entry in workshopItems:
        urls={}
        tags=[]
        if counter<=1:
            counter += 1
            continue

        if (len(entry) == 0):
            continue
        counter += 1
        summary = ""


        if '\n' in entry[0]:
            (name, summary) = entry[0].split('\n')
        else:
            code = entry[0]
            

        links = workshopLinks

        if (len(links) > counter-1 and "values" in links[counter-1]):
            urlcheck = links[counter-1]["values"]
            addurl = ""
            getLinks(urlcheck,urls)

        if (len(entry) >= 8):
            taglist = entry[7].replace(" ","\n").replace(",","\n").split('\n')
            for tag in taglist:
                if ((p.match(tag)) and tag.lower() not in tags):
                    tags.append(tag.lower())

        newtags = []

        for tag in tags:
            if not (p.match(item)):
                continue
            newtags.append(tag)

        
        new_item = {
            "code":entry[0],
            "category":"workshop",
            "name":entry[2].replace("\n", ""),
            "tags":newtags,
            "urls":urls
        }

        entries.append(new_item)

    for index in range(len(entries)):
        readme = ""
        keys = {}
        entry = entries[index]
        if ("github" in entry["urls"]):
            for url in entry["urls"]["github"]:
                if "github" not in url:
                    continue
                owner = url.split('/')[3]
                reponame = url.split('/')[4]
                repo = g.get_repo(owner + "/" + reponame)
                #try:
                #    readme = repo.get_contents("README.md")
                #except:
                #    continue
                #readmecontents = readme.decoded_content.decode()
                #entries[index]["readme"] = readmecontents
                
    for index in range(len(entries)):
        astrajson = ""
        keys = {}
        entry = entries[index]
        if ("github" in entry["urls"]):
            for url in entry["urls"]["github"]:
                if "github" not in url:
                    continue
                owner = url.split('/')[3]
                reponame = url.split('/')[4]
                repo = g.get_repo(owner + "/" + reponame)
                try:
                    astrajson = repo.get_contents("astra.json")
                except:
                    continue
                settings = json.loads(astrajson.decoded_content.decode())
                print(json.dumps(settings, indent=5))
                keys = settings.keys()
                for key in keys:
                    lowerkey = key.lower()
                    if (key.upper() == "GITHUBURL"):
                        continue
                    elif (key.upper() == "GITPODURL"):
                        entries[index]["urls"]["gitpod"] = [settings[key]]
                    elif (key.upper() == "NETLIFYURL"):
                        entries[index]["urls"]["netlify"] =[settings[key]]
                    elif (key.upper() == "DEMOURL"):
                        entries[index]["urls"]["demo"] = [settings[key]]
                    elif (key.upper() == "VERCELURL"):
                        entries[index]["urls"]["vercel"] = [settings[key]]
                    elif (key.upper() == "TAGS"):
                        for tag in settings["tags"]:
                            if ("name" in tag ):
                                if (p.match(tag["name"]) and tag["name"].lower() not in entries[index]["tags"]):
                                    entries[index]["tags"].append(tag["name"].lower())
                                continue
                            if not (p.match(tag)):
                                continue
                            if ("tags" not in entries[index]):
                                entries[index]["tags"] = []
                            elif ( tag.lower() not in entries[index]["tags"]):
                                entries[index]["tags"].append(tag.lower())
                    elif (key.upper() == "STACK"):
                        if (settings[stack][0] ==""):
                            continue
                        for stack in settings["stack"]:
                            if not (p.match(stack)):
                                continue
                            if ("stack" not in entries[index]):
                                    entries[index]["stack"] = []
                            if ((p.match(stack)) and stack.lower() not in entries[index]["stack"]):
                                    entries[index]["stack"].append(stack.lower())
                            if ((p.match(stack)) and stack.lower() not in entries[index]["tags"]):
                                    entries[index]["tags"].append(stack.lower())
                    else:
                        entries[index][lowerkey] = settings[key]

    tagdict = {}

    for entry in entries:
        if "tags" in entry:
            for tag in entry["tags"]:
                if (tag == ""):
                    continue
                if tag.lower() not in tagdict:
                    tagdict[tag.lower()] = 1
                else:
                    tagdict[tag.lower()] += 1
        if "stack" in entry:
            for stack in entry["stack"]:
                if (stack == ""):
                    continue
                if stack.lower() not in tagdict:
                    tagdict[stack.lower()] = 1
                else:
                    tagdict[stack.lower()] += 1
                    
        my_collection.create(document=entry)
        print (json.dumps(entry, indent=4))

    for tag in tagdict:
        tag_collection.create(document={'name':tag, 'count':tagdict[tag]})
        print({'name':tag, 'count':tagdict[tag]})


def addURL(urlitem, index, urls):
    if index == 1:
            if "badge" not in urls:
                urls["badge"] = []
            urls["badge"].append(urlitem)
    if index == 3:
            if "slides" not in urls:
                urls["slides"] = []
            urls["slides"].append(urlitem)
    if index == 4:
            if "github" not in urls:
                urls["github"] = []
            urls["github"].append(urlitem)
    if index == 5:
            if "menti" not in urls:
                urls["menti"] = []
            urls["menti"].append(urlitem)
    if index == 6:
            if "abstract" not in urls:
                urls["abstract"] = []
            urls["abstract"].append(urlitem)
    if index == 9:
            if "youtube" not in urls:
                urls["youtube"] = []
            urls["youtube"].append(urlitem)

def getLinks(urlcheck, urls):
    for index in range(len(urlcheck)):
            if "textFormatRuns" in urlcheck[index]:
                for textFormatRuns in range(len(urlcheck[index]["textFormatRuns"])):
                    if "link" in urlcheck[index]["textFormatRuns"][textFormatRuns]["format"]:
                        urlitem = urlcheck[index]["textFormatRuns"][textFormatRuns]["format"]["link"]["uri"]
                        if ("github" in urlitem):
                            addURL(urlitem, 4, urls)
                        else:
                            addURL(urlitem, index, urls)
            if "hyperlink" in urlcheck[index]:
                urlitem = urlcheck[index]["hyperlink"]
                addURL(urlitem, index, urls)



if __name__ == '__main__':
    main()
