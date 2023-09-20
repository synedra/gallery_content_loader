from __future__ import print_function
from astrapy.client import create_astra_client
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from cmarkgfm.cmark import Options as cmarkgfmOptions
import cmarkgfm
import pycmarkgfm
from mdx_gfm import GithubFlavoredMarkdownExtension
import markdown
from bs4 import BeautifulSoup
import re
import json
from slugify import slugify
from datetime import timedelta, date, datetime, timezone
import requests
import os.path
import os
from octohub.connection import Connection

from dotenv import load_dotenv

load_dotenv()

conn = Connection(os.environ["GITHUB_TOKEN"])
astra_client = create_astra_client(
                                    astra_database_id=os.environ["ASTRA_DB_ID"],
                                    astra_database_region=os.environ["ASTRA_DB_REGION"],
                                    astra_application_token=os.environ["ASTRA_DB_APPLICATION_TOKEN"])


applications = {}
readmes = {}
videos = {}
tag_collection = astra_client.collections.namespace(
    "gallery").collection("tag_applications")
readme_collection = astra_client.collections.namespace(
    "gallery").collection("readme_applications")
video_collection = astra_client.collections.namespace(
    "gallery").collection("video_applications")


# using an access token

token = os.environ["GITHUB_TOKEN"]
headers = {'Authorization': f'token {token}'}

p = re.compile('[a-zA-Z]+')

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/youtube.force-ssl', "https://www.googleapis.com/auth/youtube.readonly"]
SAMPLE_SPREADSHEET_ID = '1vJSKJAa7EJ0s1Ksn_L_lgQGJI6-UMDqNngrQO4U4cEY'
SAMPLE_RANGE_NAME = 'SampleApplicationMain'

def main():
    service, youtube = getCreds()
    sampleApplicationItems, sampleApplicationLinks, workshopItems, workshopLinks = getWorksheetInfo(
        service)

    entries = processApplicationItems(
        sampleApplicationItems, sampleApplicationLinks, [])
    entries = processWorkshopItems(workshopItems, workshopLinks, entries)
    entries = processGithubOrganization('DatastaxDevs', entries)
    entries = processGithubOrganization('Datastax-Examples', entries)
    entry = {"urls":{"github":["https://github.com/cassioml/langchain-flare-pdf-qa-demo"]},"tags":["starter"],"name":"PDF FLARE demo with Langchain and Cassandra as Vector Store"}
    entries.append(entry)

    entry = {"urls":{"github":["https://github.com/DataStax-Examples/stargate-mongoose-demo-ecommerce"]},"name":"Stargate Mongoose Demo Ecommerce"}
    entries.append(entry)
    entry = {"urls":{"github":["https://github.com/DataStax-Examples/stargate-mongoose-demo-discord-bot"]},"name":"Stargate Mongoose Demo Discord Bot"}
    entries.append(entry)

    entry = {"urls":{"github":["https://github.com/DataStax-Examples/stargate-mongoose-demo-typescript-express-reviews"]},"name":"Stargate Mongoose Typescript Express Reviews"}
    entries.append(entry)

    entry = {"urls":{"github":["https://github.com/DataStax-Examples/stargate-mongoose-demo-photography"]},"name":"Stargate Mongoose Demo Photography"}
    entries.append(entry)
    entry = {"urls":{"github":["https://github.com/DataStax-Examples/astra-next.js-starter"]},"name":"Astra Next JS Starter"}
    entries.append(entry)
    entry = {"urls":{"github":["https://github.com/DataStax-Examples/glitch-astra-starter"]}, "name":"Glitch Astra Starter"}
    entries.append(entry)
    entry = {"urls":{"github":["https://github.com/DataStax-Examples/astra-nodejs-starter"]}, "name":"Astra NodeJS Starter"}
    entries.append(entry)
    entry = {"urls":{"github":["https://github.com/DataStax-Examples/astra-gatsbyjs-starter"]}, "name":"Astra GatsbyJS Starter"}
    entries.append(entry)
    entry = {"urls":{"github":["https://github.com/DataStax-Examples/google-cloud-functions-nodejs"]}, "name":"Google Cloud Functions NodeJS"}
    entries.append(entry)
    entry = {"urls":{"github":["https://github.com/DataStax-Examples/nf-data-explorer"]},"tags":["tools"], "name":"Netflix Data Explorer"}
    entries.append(entry)
    entry = {"urls":{"github":["https://github.com/datastax/astra-ide-plugin/wiki/Getting-Started"]},"tags":["tools"], "name":"Astra Jetbrains IDE"}
    entries.append(entry)
    entry = {"urls":{"github":["https://github.com/DataStax-Examples/astra-spark-migration"]},"tags":["tools"],"name":"Astra Spark Migration"}
    entries.append(entry)
    entry = {"urls":{"github":["https://github.com/DataStax-Examples/dsbulk-to-astra"]}, "tags":["tools"], "name":"Dsbulk to Astra"}
    entries.append(entry)
    # Add awesome-astra
    newvideos = recursiveSearch(youtube, '', [])
    videos = getDBVideosRecursive(newvideos)
    updateVideoStatistics(youtube, videos)

    for index in range(len(entries)):
        astrajson = ""
        entry = entries[index]
        if "tags" not in entry:
            entry["tags"] = []

        if ("github" in entry["urls"]):
            for url in entry["urls"]["github"]:
                if "github" not in url:
                    continue
                owner = url.split('/')[3]
                reponame = url.split('/')[4]

                uri = '/repos/' + owner + '/' + reponame
                print (uri)

                repo = conn.send('GET', uri)
                entry["last_modified"] = repo.parsed.updated_at
                entry["stargazers"] = repo.parsed.stargazers_count
                entry["forks"] = repo.parsed.forks_count
                if repo.parsed.description:
                    entry["description"] = repo.parsed.description

                uri = '/repos/' + owner + '/' + reponame
                print (uri)

                reposlug = owner + "-" + reponame
                
                astrajson = ""
                print("Getting astra.json for " +
                          owner + "/" + reponame + " at 99")
                astrajson = requests.get('https://raw.githubusercontent.com/' + owner + '/' + reponame + '/main/astra.json')
                if (astrajson.status_code != 404):
                    entry = astraJsonSettings(json.loads(
                        astrajson.text), entry)

                # Direct conversion
                options = (
                        cmarkgfmOptions.CMARK_OPT_HARDBREAKS
                        | cmarkgfmOptions.CMARK_OPT_UNSAFE
                        | cmarkgfmOptions.CMARK_OPT_GITHUB_PRE_LANG
                        )
                try:
                    readme = requests.get('https://raw.githubusercontent.com/' + owner + '/' + reponame + '/main/README.md')
                    if readme.status_code == 404:
                        readme = requests.get('https://raw.githubusercontent.com/' + owner + '/' + reponame + '/master/README.md')
                    
                    html = cmarkgfm.github_flavored_markdown_to_html(readme.text, options)
                    #print("\n\n\nSTARTING HTML for " + reposlug + " : \n\n" + html)
                    
                    newhtml = ""
                    headerpattern = re.compile("((<h.>)(.+?)(<\/h.>))")
                    srcpattern=re.compile("(src=\"(.+?)\")")
                    httppattern = re.compile("http")
                    linkpattern=re.compile("href=(\".+?\")")
                    poundpattern=re.compile("(#)")

                    
                    for line in html.splitlines():
                        match = headerpattern.search(line)
                        if match:
                            slug = slugify(match.group(3))
                            anchorline = match.group(2) + '<a class="anchor" aria-hidden="true" id="' + slug + '"> </a>' + match.group(3) + match.group(4)

                            line = line.replace(match.group(0), anchorline)

                        srcmatch = srcpattern.search(line)
                        httpmatch = httppattern.search(line)
                        if srcmatch and not httpmatch:
                            replace = "https://github.com/" + owner + "/" + reponame + "/raw/master/" +  srcmatch.group(2)
                            line = line.replace(srcmatch.group(2), replace)

                        linkmatch = linkpattern.search(line)
                        if linkmatch:
                            replace = linkmatch.group(1) + " target=\"_blank\""
                            line = line.replace(linkmatch.group(1), replace)
                        
                        newhtml += line + "\n"

                    print("HTML FOR " + reposlug)
                    res = readme_collection.create(document={"content":newhtml}, path=reposlug)
                    print("SUCCESS SAVING README for " + reposlug)
                except:
                    print("ERROR SAVING README for " + reposlug)
                
                try:
                    for tag in repo.get_topics():
                        entries[index]["tags"].append(tag)
                except:
                    print("No gh tags for" + reposlug)

                if "categories" in entry:
                    for tag in entry["categories"]:
                        entries[index]["tags"].append(tag)

                if "starter" in repo.url:
                    entries[index]["tags"].append("starter")
                    print("Added to starter - " + json.dumps(entry))
                
                entries[index]["tags"] = cleanTags(entries[index]["tags"])

    tagdict = {}
    tagdict["all"] = {}
    tagdict["all"]["apps"] = []
    names = []

    for entry in entries:
        
        if "tags" in entry:
            for tag in entry["tags"]:
                if tag.lower() not in tagdict.keys():
                    tagdict[tag.lower()] = {
                        "name": tag.lower(), "apps": [entry]}
                    if entry["name"] not in names:
                        tagdict["all"]["apps"].append(entry)
                        names.append(entry["name"])
                else:
                    tagdict[tag.lower()]["apps"].append(entry)
                    if entry["name"] not in names:
                        tagdict["all"]["apps"].append(entry)
                        names.append(entry["name"])
            

    for tag in tagdict.keys():
        count = len(tagdict[tag]["apps"])
        tagdict[tag]["count"] = count

        try:
            res = tag_collection.create(
                document={"name": tag, "count": count, tag: tagdict[tag]}, path=tag)
            print("SUCCESS for " + tag)
            print(json.dumps(res))
        except:
            print("ERROR for " + tag)
            print(json.dumps(res))


def cleanTags(tags):
    newtags = []
    for tag in tags:
        if not (p.match(tag)):
            continue
        if tag in ("doc api", "document-api", "stargate documents api", "doc-api", "documentapi", "docapi", "document api"):
            tag = "doc api"
        if tag in ("rest-api"):
            tag = "rest api"
        if tag in ("grpc"):
            tag = "grpc api"
        if tag in ("gql api", "graphql"):
            tag = "graphql api"
        if tag in ("nodejs", "nodejs driver","nodejs-driver"):
            tag = "nodejs"
        if tag in ("python", "python driver"):
            tag = "python"
        if tag in ("java", "java driver", "java-driver"):
            tag = "java"
        if tag in ("reactjs", "react-native"):
            tag = "react"
        if tag in ("ml", "machine-learning"):
            tag = "machine learning"
        if tag in ("datastax-enterprise"):
            tag = "dse"
        if tag in ("astra", "astra db"):
            tag = "astradb"
        if tag in ("apache cassandra", "cassandra-database","apache-cassandra"):
            tag = "cassandra"
        if tag in ("spring-data-cassandra","spring-mvc","spring-boot", "spring-data", "spring", "spring-webflux"):
            tag = "spring"
        if tag not in newtags:
            newtags.append(tag)
    
    return newtags

def addURL(urlitem, index, urls):
    if index == 1:
        if "badge" not in urls:
            urls["badge"] = []
        urls["badge"].append(urlitem)
        urls["heroimage"] = urlitem
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

def astraJsonSettings(settings, entry):
    keys = settings.keys()
    if "tags" not in entry:
        entry["tags"] = []
    for key in keys:
        lowerkey = key.lower()
        if (key.upper() == "GITHUBURL"):
            continue
        elif (key.upper() == "GITPODURL"):
            entry["urls"]["gitpod"] = [settings[key]]
        elif (key.upper() == "NETLIFYURL"):
            entry["urls"]["netlify"] = [settings[key]]
        elif (key.upper() == "DEMOURL" or key.upper() == "DEMO"):
            entry["urls"]["demo"] = [settings[key]]
        elif (key.upper() == "VERCELURL"):
            entry["urls"]["vercel"] = [settings[key]]
        elif (key.upper() == "YOUTUBEURL"):
            if  isinstance(settings[key], str):
                entry["urls"]["youtube"] = [settings[key]]
            else:
                entry["urls"]["youtube"] = settings[key]
        elif (key.upper() == "TAGS"):
            for tag in settings["tags"]:
                if ("name" in tag):
                    entry["tags"].append(
                        tag["name"].lower())
                else:
                    entry["tags"].append(tag.lower())
        elif (key.upper() == "STACK"):
            for stack in settings["stack"]:
                if ("tags" not in entry):
                    entry["tags"] = []
                entry["tags"].append(stack.lower())
        elif (key.upper() == "CATEGORY"):
            entry["tags"].append(settings[key])
        elif (key.upper() == "HEROIMAGE"):
            entry["urls"]["heroimage"] = settings[key]
        else:
            entry[lowerkey] = settings[key]
    if "tags" in entry:
        entry["tags"] = cleanTags(entry["tags"])
    return entry

def getCreds():
    print("Starting Creds")
    entries = []
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(os.environ['GOOGLE_TOKEN_FILE']):
        creds = Credentials.from_authorized_user_file(os.environ['GOOGLE_TOKEN_FILE'], SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing creds")
            try:
                creds.refresh(Request())
            except:
                print("ERROR")
        else:
            print("Using creds")
            flow = InstalledAppFlow.from_client_secrets_file(
                os.environ['CLIENT_SECRET_FILE'], SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(os.environ['GOOGLE_TOKEN_FILE'], 'w') as token:
            token.write(creds.to_json())
    service = build('sheets', 'v4', credentials=creds)
    youtube = build('youtube', 'v3', credentials=creds)
    return service, youtube

def getWorksheetInfo(service):   
    sheet = service.spreadsheets()

    print("Getting sample application links")
    # Call the Sheets API for SampleApplication links
    result = service.spreadsheets().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, ranges=SAMPLE_RANGE_NAME,
                                        fields="sheets/data/rowData/values/hyperlink,sheets/data/rowData/values/textFormatRuns/format/link/uri").execute()
    values = result.get('sheets', [])

    sampleApplicationLinks = values[0]["data"][0]["rowData"]
    print("Got sample application links")

    print("Getting sample application items")
    # Call the Sheets API for SampleApplication items
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    sampleApplicationItems = result.get('values', [])
    print("Got sample application items")
    # Workshop sheet for links
    WORKSHOP_SAMPLE_RANGE_NAME = 'WorkshopCatalog'

    print("Getting workshop links")
    # Call the Sheets API for Workshop Links
    result = service.spreadsheets().get(spreadsheetId=SAMPLE_SPREADSHEET_ID, ranges=WORKSHOP_SAMPLE_RANGE_NAME,
                                        fields="sheets/data/rowData/values/hyperlink,sheets/data/rowData/values/textFormatRuns/format/link/uri").execute()
    values = result.get('sheets', [])
    workshopLinks = values[0]["data"][0]["rowData"]

    print("Got workshop links")
    print("Getting workshop items")
    # Get the items for Workshops
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=WORKSHOP_SAMPLE_RANGE_NAME).execute()
    workshopItems = result.get('values', [])
    print("Got workshop items")
 
    return (sampleApplicationItems, sampleApplicationLinks, workshopItems, workshopLinks)

def processWorkshopItems(workshopItems, workshopLinks, entries):
    counter = 0
    for entry in workshopItems:
        urls = {}
        tags = []
        if counter <= 1:
            counter += 1
            continue

        if (len(entry) == 0):
            continue
        counter += 1
        description = ""

        
        if '\n' in entry[0]:
            (name, description) = entry[0].split('\n')
            code = ""
        else:
            code = entry[0]

        links = workshopLinks

        if (len(links) > counter-1 and "values" in links[counter-1]):
            urlcheck = links[counter-1]["values"]
            addurl = ""
            getLinks(urlcheck, urls)

        if (len(entry) >= 8):
            taglist = entry[7].replace(',', "\n").split('\n')
            for tag in taglist:
                tags.append(tag.lower())

        tags.append("workshop")
        newtags = cleanTags(tags)

        new_item = {
            "code": code,
            "name": entry[2].replace("\n", ""),
            "tags": newtags,
            "urls": urls
        }
        
        entries.append(new_item)
    return entries


def processApplicationItems(sampleApplicationItems, sampleApplicationLinks, entries):
    counter = 0
    for entry in sampleApplicationItems:
        urls = {"heroimage":"https://yt3.googleusercontent.com/ytc/AMLnZu99z7O76h-EBAOloogUjeaXsi0HN-2YaiixWxAjyw=s176-c-k-c0x00ffffff-no-rj-mo"}
        if counter == 0:
            counter += 1
            continue

        counter += 1
        description = ""
        if '\n' in entry[0]:
            (name, description) = entry[0].split('\n')
        else:
            if entry[0] == "":
                continue
            name = entry[0]

        links = sampleApplicationLinks
        if (len(links) > counter-1 and "values" in links[counter-1]):
            urlcheck = links[counter-1]["values"]
            getLinks(urlcheck, urls)

        tags = []
        language = []
       # Language
        if (entry[2] != [""]):
            language = entry[2].split(",")
            for item in language:
                tags.append(item.lower())

        # Stack should be an array
        if (entry[3] != [""]):
            stack = entry[3].split(",")
            for item in stack:
                tags.append(item.lower())

        # APIs
        entrynumber = 6
        apiarray = []
        for api in ["DATA", "DOC", "GQL", "CQL", "GRPC", "DB", "IAM", "STRM"]:
            if entry[entrynumber] == 'TRUE':
                apiarray.append(api)
            entrynumber += 1

        newtags = cleanTags(tags)

        new_item = {
            "name": name,
            "description": description,
            "urls": urls,
            "language": language,
            "stack": stack,
            "usecases": entry[4],
            "owner": entry[5],
            "apis": apiarray,
            "tags": newtags
        }

        entries.append(new_item)
    return entries

def processGithubOrganization(org, entries):
    uri = '/orgs/' + org + '/repos'

    repos = conn.send('GET', uri)

    for repo in repos.parsed:
        owner = repo.owner.login
        reponame = repo.name
        url = repo.html_url
        reposlug = owner + '-' + reponame

        try:
            astrajson_path = "/repos/" + owner + "/" + reponame + "/contents/astra.json"
            astrajson = conn.send('GET', astrajson_path)
            astraparsed = astrajson.parsed
        except:
            continue

        entry = {"urls":{"github":[url]}}
        entries.append(entry)
    return entries

def updateVideoStatistics(youtube, videos):
    for videoId in videos:
        request = youtube.videos().list(
            part="statistics, liveStreamingDetails",
            id=videoId
        )
        response = request.execute()

        try:
            res = video_collection.create(
                document=response["items"][0], path=videoId)
            print("SUCCESS for " + videoId)
            print(json.dumps(response["items"][0]))
        except:
            print("ERROR for " + videoId)
            print(json.dumps(res))


def getDBVideosRecursive(videos, pagestate=None):
    res = None
    if pagestate:
        res = video_collection.find({}, {"page-state": pagestate})
    else:
        res = video_collection.find({})

    for video in res["data"].values():
        videos.append(video["id"])

    return videos


def recursiveSearch(youtube, nextPage, videos=[]):
    lastweek = datetime.utcnow() - timedelta(7)
    lastweek = lastweek.isoformat()[:-3]
    lastweek = str(lastweek) + "Z"

    if nextPage:
        request = youtube.search().list(
            part="id, snippet",
            channelId="UCAIQY251avaMv7bBv5PCo-A",
            pageToken=nextPage,
            type="video",
            publishedAfter=lastweek,
            maxResults=50
        )
    else:
        request = youtube.search().list(
            part="id, snippet",
            type="video",
            channelId="UCAIQY251avaMv7bBv5PCo-A",

            maxResults=50
        )

    response = request.execute()
    for video in response['items']:
        videos.append(video["id"]["videoId"])
    if "nextPageToken" in response:
        recursiveSearch(youtube, response['nextPageToken'], videos)

    return (videos)

if __name__ == '__main__':
    main()
