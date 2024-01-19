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

demo_collection = AstraDBCollection(collection_name="tag_gallery", astra_db=astra_db)


def main():
    insert = {
        "_id": "languages",
        "tags":[
          "javascript",
          "csharp",
          "java",
          "nodejs",
          "python",
          "c#",
          "scala",
          "ios",
          "android",
        ]}
   # demo_collection.delete_one(id="languages")
   # demo_collection.insert_one(insert)
    insert = {
        "_id":"apis", "tags":[
          "doc api",
          "graphql api",
          "rest api",
          "gprc api",
          "devops-apis",
          "json-api",
        ]}
   # demo_collection.delete_one(id="apis")
    
   # demo_collection.insert_one(insert)
    insert = {
        "_id":"secret", "tags": ["workshop", "apps", "starters", "dev", "tools", "examples"]
    }
    #demo_collection.delete_one(id="secret")
    
    #demo_collection.insert_one(insert)
    insert = {
        "_id":"frameworks", 
        "tags":[
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
        ]
    }
    print(insert)
    demo_collection.delete_one(id="frameworks")
    
    demo_collection.insert_one(insert)
    insert={"_id":"technology", "tags":[
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
        ]}
 #   demo_collection.delete_one(id="technology")
    
 #   demo_collection.insert_one(insert)
    insert = {"_id":"integrations", "tags":
                  [
          "eddiehub",
          "jamstack",
          "netlify",
          "gitpod",
          "template",
          "google-cloud",
        ]}
#    demo_collection.delete_one(id="integrations")
    
#    demo_collection.insert_one(insert)
    insert = {"_id":"usecases", "tags":[
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
          "devops",
        ]   }
    demo_collection.delete_one(id="usecases")
    
    demo_collection.insert_one(insert)
if __name__ == '__main__':
    main()
