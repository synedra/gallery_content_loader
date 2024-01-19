from github import Github
import cassio
from langchain_community.vectorstores import Cassandra
from langchain.schema import Document
import cmarkgfm
from cmarkgfm.cmark import Options as cmarkgfmOptions
import requests
from openai import OpenAI
from astrapy.db import AstraDB, AstraDBCollection
from astrapy.ops import AstraDBOps

import json
import os.path
import os
import re
from dotenv import load_dotenv
load_dotenv()

# using an access token
f = open("github.token", "r")
line = f.readlines()[0].replace("\n", "")
g = Github(line)

p = re.compile('[a-zA-Z]+')
token = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
api_endpoint = os.getenv("ASTRA_DB_API_ENDPOINT")

# Initialize our vector db
astra_db = AstraDB(token=token, api_endpoint=api_endpoint)

#astra_db.create_collection(collection_name="tag_gallery", dimension=1536)
#astra_db.create_collection(collection_name="readme_gallery", dimension=1536)

demo_collection = AstraDBCollection(collection_name="application_gallery", astra_db=astra_db)
tag_collection = AstraDBCollection(collection_name="tag_gallery", astra_db=astra_db)
readme_collection = AstraDBCollection(collection_name="readme_gallery", astra_db=astra_db)

tag_collection.delete_one(id="alltags")

os.environ['OPENAI_API_TYPE'] = "open_ai"
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
embedding_model_name = "text-embedding-ada-002"

taglist = []

# using an access token
f = open("github.token", "r")
line = f.readlines()[0].replace("\n", "")
g = Github(line)

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
    "machine learning",
    "graph",
    "ai",
    "game",
    "performance testing",
    "ds-bulk",
    "timeseries db",
    "killrvideo",
    "devops"]


def main():
    # Grab the Astra token and api endpoint from the environment
    counter = 0
    input_documents = []
    
    from langchain_openai import OpenAIEmbeddings
    myEmbedding = OpenAIEmbeddings()

    processOrganization('Datastax-Examples')
    processOrganization('DatastaxDevs')
    #tagset = set(taglist)
    #newtagset = list(tagset)
    #print (newtagset)
    #
    #tag_collection.insert_one({"_id":"other", "taglist":newtagset})

def processOrganization(organization_name):

    github = {}
    entries = []
    
    organization = g.get_organization(organization_name)
    astrajson = ""
    readme_as_a_string = ""
        
    for repo in organization.get_repos():
        url = repo.raw_data["html_url"]
        keyname = organization_name + "-" + repo.raw_data["name"]
        rawkey = repo.raw_data["name"]
        print ("Keyname: " + keyname)
        try:
            astrajson = repo.get_contents("astra.json")
            print("Got astra.json")

        except:
            continue

        options = (
                        cmarkgfmOptions.CMARK_OPT_HARDBREAKS
                        | cmarkgfmOptions.CMARK_OPT_UNSAFE
                        | cmarkgfmOptions.CMARK_OPT_GITHUB_PRE_LANG
                        )
        
        try:
            print ("Trying to get readme")
            firstrepo = 'https://raw.githubusercontent.com/' + organization_name + '/' + rawkey + '/main/README.md'
            print(firstrepo)
            readme = requests.get(firstrepo)
            if readme.status_code == 404:
                secondrepo = 'https://raw.githubusercontent.com/' + organization_name  + '/' + rawkey + '/master/README.md'
                readme = requests.get(secondrepo)
            
                if readme.status_code == 404:
                    print("Couldn't find a readme")
                    continue
            readme_as_a_string = cmarkgfm.github_flavored_markdown_to_html(readme.text, options)
            print(readme_as_a_string)
            query_vector = client.embeddings.create(
                input=[readme_as_a_string],
                model=embedding_model_name).data[0].embedding
            readme_entry = {}
            readme_entry["$vector"] = query_vector
            readme_entry["_id"] = entry["key"]
            readme_entry["readme"] = readme_as_a_string
            readme_collection.insert_one(readme_entry)
            print("Inserted readme")

        except:
            readme_as_a_string = ""
        
        if (astrajson is not None):
                entry = {"tags":[], "urls":{"github":url}}
                
                settings = json.loads(astrajson.decoded_content.decode())
                keys = settings.keys()
                entry["key"] = keyname
                for key in keys:
                    lowerkey = key.lower()
                    if (key.upper() == "GITHUBURL"):
                        continue
                    elif (key.upper() == "GITPODURL"):
                        entry["urls"]["gitpod"] = settings[key]
                    elif (key.upper() == "NETLIFYURL"):
                        entry["urls"]["netlify"] = settings[key]
                    elif (key.upper() == "DEMOURL"):
                        entry["urls"]["demo"] = settings[key]
                    elif (key.upper() == "VERCELURL"):
                        entry["urls"]["vercel"] = settings[key]
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
        if "name" in entry:
            filename = entry["key"] + ".json"
            print(filename)
            with open(filename, 'w') as outfile:
                json.dump(entry, outfile, indent=4)
                print("Wrote " + filename)

            vector_json = json.dumps(entry)
            query_vector = client.embeddings.create(input=[vector_json],
    model=embedding_model_name).data[0].embedding
            entry["$vector"] = query_vector
            entry["_id"] = entry["key"]
            for tag in entry["tags"]:
                if tag not in existingtags:
                    taglist.append(tag)
                    print(taglist)

            print("ENTRY:" + json.dumps(entry))
            response = demo_collection.insert_one(entry)
            print("RESPONSE:" + json.dumps(response))
                
    

def cleanTags(tags):
    newtags = []
    for tag in tags:
        if not (p.match(tag)):
            continue
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


if __name__ == '__main__':
    main()
