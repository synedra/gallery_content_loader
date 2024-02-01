from github import Github
import cassio
from langchain_community.vectorstores import Cassandra
from langchain.schema import Document
import cmarkgfm
from cmarkgfm.cmark import Options as cmarkgfmOptions
import requests
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from openai import OpenAI
from astrapy.db import AstraDB, AstraDBCollection
from astrapy.ops import AstraDBOps
from pytube import extract

SCOPES = [ "https://www.googleapis.com/auth/youtube.readonly"]

import json
import os.path
import base64
import os
import re
from dotenv import load_dotenv
load_dotenv()

g = Github(os.getenv("GITHUB_TOKEN"))

p = re.compile('[a-zA-Z]+')
token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")
    
# Initialize our vector db
astra_db = AstraDB(token=token, api_endpoint=api_endpoint)

#astra_db.create_collection(collection_name="tag_gallery", dimension=1536)
#astra_db.create_collection(collection_name="readme_gallery", dimension=1536)
#astra_db.create_collection(collection_name="application_gallery", dimension=1536)
#astra_db.delete_collection(collection_name="application_gallery")
#astra_db.create_collection(collection_name="application_gallery", dimension=1536)

demo_collection = AstraDBCollection(collection_name="application_gallery", astra_db=astra_db)
tag_collection = AstraDBCollection(collection_name="tag_gallery", astra_db=astra_db)
readme_collection = AstraDBCollection(collection_name="readme_gallery", astra_db=astra_db)

tag_collection.delete_one(id="alltags")

os.environ['OPENAI_API_TYPE'] = "open_ai"
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
embedding_model_name = "text-embedding-ada-002"

taglist = []

# using an access token
g = Github(os.getenv("GH_TOKEN"))

p = re.compile('[a-zA-Z]+')
token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")

# Initialize our vector db
astra_db = AstraDB(token=token, api_endpoint=api_endpoint)

existingtags = [
    "javascript",
    "csharp",
    "java",
    "nodejs",
    "python",
    "c#",
    "scala",
    "ios",
    "android",
    "doc api",
    "graphql api",
    "rest api",
    "gprc api",
    "devops-apis",
    "json-api",
    "workshop", 
    "apps", 
    "starters", 
    "dev", 
    "tools", 
    "examples"
    "selenium",
    "react",
    "spring",
    "mongoose",
    "django",
    "nextjs",
    "nestjs",
    "angular",
    "redux",
    "webflux",
    "elixir",
    "serverless-framework",
    "streaming",
    "video",
    "kubernetes",
    "k8ssandra",
    "cql",
    "nosql",
    "vector",
    "astradb",
    "dse",
    "cassandra",
    "fastapi",
    "datastax",
    "keyspaces",
    "eddiehub",
    "jamstack",
    "netlify",
    "gitpod",
    "template",
    "google-cloud",
    "change data capture",
    "building-sample-apps",
    "ansible-playbooks",
    "machine-learning",
    "ai",
    "game",
    "performance testing",
    "ds-bulk",
    "timeseries db",
    "killrvideo",
    "devops"]


def main():


    print(os.getenv("TOKEN_JSON"))
    tokenjson = json.dumps(os.getenv("TOKEN_JSON"))
    
    with open('token.json', 'w') as token_json:
        token_json.write(tokenjson)
        print(tokenjson)

    with open('credentials.json', 'w') as credentials_json:
        credentialsjson = json.dumps(os.getenv("CREDENTIALS_JSON"))
        print(credentialsjson)
        credentials_json.write(credentialsjson)
        print(credentialsjson)


    os.system('ls -al')
    os.system('cat token.json')

    # Grab the Astra token and api endpoint from the environment
    counter = 0
    input_documents = []

    youtube = getCreds()
    
    from langchain_openai import OpenAIEmbeddings
    myEmbedding = OpenAIEmbeddings()

    astrajson = ""
    readme_as_a_string = ""

    options = (
                        cmarkgfmOptions.CMARK_OPT_HARDBREAKS
                        | cmarkgfmOptions.CMARK_OPT_UNSAFE
                        | cmarkgfmOptions.CMARK_OPT_GITHUB_PRE_LANG
                        )
        
    repo = g.get_repo("datastaxdevs/gallery_content_loader")    
    contents = repo.get_contents("astrajson")
    for content_file in contents:
        readme_trunc = ""
        print(content_file)
        
        if content_file.name.endswith(".json"):
            print("Getting " + content_file.name)
            astrajson = content_file
            last_modified = content_file.last_modified
            currententry = json.loads(content_file.decoded_content.decode())
            if ("$vector" in currententry):
                del currententry["$vector"]
            repository = currententry["urls"]["github"]
            url = currententry["urls"]["github"]
            organization_name = repository.split("/")[3]
            repository_name = repository.split("/")[4]
            key = currententry["key"]
            if ("last_modified" in currententry and currententry["last_modified"] == last_modified):
                print ("No update, skipping " + content_file.name)
                continue

            try:
                firstrepo = 'https://raw.githubusercontent.com/' + organization_name + '/' + repository_name + '/main/README.md'
                readme = requests.get(firstrepo)
                if readme.status_code == 404:
                    secondrepo = 'https://raw.githubusercontent.com/' + organization_name  + '/' + repository_name + '/master/README.md'
                    readme = requests.get(secondrepo)

                readme_as_a_string = cmarkgfm.github_flavored_markdown_to_html(readme.text, options)
                readme_entry = {}
                #readme_entry["$vector"] = query_vector
                readme_entry["_id"] = currententry["key"]
                readme_entry["readme"] = readme_as_a_string
                readme_trunc = readme_as_a_string[:5000]

                try:
                    readme_collection.insert_one(readme_entry)
                    print("Inserted readme for " + currententry["key"])
                except:
                    readme_collection.find_one_and_replace(filter={"_id":currententry["key"]}, replacement=readme_entry)
                    print("Replaced readme for  " + currententry["key"])
            except(Exception) as error:
                print(error)
                continue

        if (astrajson is not None):
            apprepo = g.get_repo(organization_name  + '/' + repository_name)
            last_modified = apprepo.last_modified
            forks_count = apprepo.forks_count
            stargazers_count = apprepo.stargazers_count
            ghtopics = apprepo.get_topics()
            for topic in ghtopics:
                if topic not in currententry["tags"]:
                    currententry["tags"].append(topic)
            
            newentry = {"key":key, "tags":currententry["tags"], "urls":{"github":url}, "last_modified":last_modified, "forks_count":forks_count, "stargazers_count":stargazers_count}
            
            settings = json.loads(astrajson.decoded_content.decode())
            keys = settings.keys()
            for key in keys:
                lowerkey = key.lower()
                if (key.upper() == "GITHUBURL"):
                    continue
                elif (key.upper() == "YOUTUBEURL" or key.upper() == "YOUTUBE"):
                    print("Youtube is " + json.dumps(settings[key]))
                    newentry["urls"]["youtube"] = settings[key]
                    try:
                        (path, video_id) = settings[key][0].split("=")
                        (likes, views) = getVideoStats(youtube, video_id)
                        newentry["likes"] = likes
                        newentry["views"] = views
                    except:
                        continue
                elif (key.upper() == "GITPODURL"):
                    newentry["urls"]["gitpod"] = settings[key]
                elif (key.upper() == "NETLIFYURL"):
                    newentry["urls"]["netlify"] = settings[key]
                elif (key.upper() == "DEMOURL"):
                    newentry["urls"]["demo"] = settings[key]
                elif (key.upper() == "VERCELURL"):
                    newentry["urls"]["vercel"] = settings[key]
                elif (key.upper() == "TAGS"):
                    for tag in settings["tags"]:
                        if ("name" in tag):
                            newentry["tags"].append(
                                tag["name"].lower())
                        else:
                            newentry["tags"].append(tag.lower())
                elif (key.upper() == "STACK"):
                    for stack in settings["stack"]:
                        if ("tags" not in entry):
                            newentry["tags"] = []
                        newentry["tags"].append(stack.lower())
                elif (key.upper() == "CATEGORY"):
                    newentry["tags"].append(settings[key])
                elif (key.upper() == "HEROIMAGE"):
                    newentry["urls"]["heroimage"] = settings[key]
                else:
                    newentry[lowerkey] = settings[key]
            newentry["readme"] = readme_trunc
            if ("$vector" in newentry):
                del newentry["$vector"] 
            vector_json = json.dumps(newentry)
            
            for tag in newentry["tags"]:
                if tag not in existingtags:
                    taglist.append(tag)
            
            newentry["tags"] = cleanTags(newentry["tags"])

            query_vector = client.embeddings.create(input=[vector_json],
                model=embedding_model_name).data[0].embedding
            newentry["_id"] = newentry["key"]
            newentry["$vector"] = query_vector
            
            try:
                demo_collection.insert_one(newentry)
                print("Inserted " + newentry["key"])
            except:
                demo_collection.find_one_and_replace(filter={"_id":newentry["key"]}, replacement=newentry)
                print("Replaced " + newentry["key"])

            filename = "./astrajson/" + newentry["key"] + ".json"
            del newentry["$vector"]
            with open(filename, 'w') as outfile:
                json.dump(newentry, outfile, indent=4)
                print("Wrote " + filename)
        

def cleanTags(tags):
    newtags = []
    for tag in tags:
        if not (p.match(tag)):
            continue
        if tag in ("astra", "astra db", "astradb"):
            tag = "astradb"
        if tag in ("doc api", "documentapi", "docapi", "document api"):
            tag = "doc api"
        if tag in ("gql api", "graphql"):
            tag = "graphql api"
        if tag in ("java", "java driver"):
            tag = "java"
        if tag in ("spring-boot", "spring-data", "spring", "spring-webflux"):
            tag = "spring"
        if tag not in newtags:
            newtags.append(tag)
    return newtags

def getVideoId(youtubeurl):
    from pytube import extract
    id=extract.video_id(youtubeurl)
    return(id)

def getVideoStats(youtube, videoid):
    print("Getting stats for video")
    request = youtube.videos().list(
            part="statistics, liveStreamingDetails",
            id=videoid
    )
    response = request.execute()
    print(response) 
    try:
        (likes, views) = response["items"][0]["statistics"]["likeCount"], response["items"][0]["statistics"]["viewCount"]
        return(likes, views)
    except:
        return(0,0)

def getCreds():
    print("Starting Creds")
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
            print("Refreshing creds")
            creds.refresh(Request())
        else:
            print("Using creds")
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    youtube = build('youtube', 'v3', credentials=creds)
    return youtube

def decode_and_parse_credentials(encoded_credentials):
    try:
        while len(encoded_credentials) % 4 != 0:
            encoded_credentials += '='
        
        # Decode the base64 string to bytes
        credentials_bytes = base64.b64decode(encoded_credentials)
        
        # Convert bytes to a JSON string
        credentials_str = credentials_bytes.decode('utf-8')
        
        # Parse the JSON string into a dictionary
        credentials = json.loads(credentials_str)
        
        return credentials
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    main()
