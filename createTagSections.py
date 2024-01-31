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
astra_db.delete_collection(collection_name="tag_gallery")
astra_db.create_collection(collection_name="tag_gallery", dimension=1536)

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
        ]}
    demo_collection.delete_one(id="languages")
    response = demo_collection.insert_one(insert)
    print(response)
    insert = {
        "_id":"apis", "tags":[
          "doc api",
          "graphql api",
          "rest api",
          "gprc api",
          "devops-apis",
          "json-api",
          "stargate documents api",
          "api"
        ]}

    response = demo_collection.insert_one(insert)
    print(response)  
    insert = {
        "_id":"secret", "tags": ["workshop", "apps", "starters", "dev", "tools", "examples"]
    }
    demo_collection.delete_one(id="secret")
    
    response = demo_collection.insert_one(insert)
    print(response)
    insert = {
        "_id":"frameworks", 
        "tags":[
          "selenium",
          "react",
          "pandas",
          "spring",
          "stargate-mongoose",
          "mongoose",
          "django",
          "nextjs",
          "nestjs",
          "nuxtjs",
          "helm",
          "angular",
          "redux",
          "webflux",
          "elixir",
          "serverless-framework",
          "video",
          "pulsar",
          "express"
        ]
    }
    response = demo_collection.insert_one(insert)
    print(response)
    insert={"_id":"technology", "tags":[
          "kubernetes",
          "k8ssandra",
          "cql",
          "nosql",
          "vector",
          "astradb",
          "cassandra",
          "fastapi",
          "datastax",
          "stargate",
          "keyspaces",
          "astrastreaming",
          "ios",
          "android"
        ]}
    demo_collection.delete_one(id="technology")
    
    response = demo_collection.insert_one(insert)
    print(response)
    insert = {"_id":"integrations", "tags":
                  [
          "eddiehub",
          "jamstack",
          "netlify",
          "gitpod",
          "template",
          "google-cloud",
          "docker",
          "selenium",
          "pyspark",
          "nodejs driver"
        ]}
    demo_collection.delete_one(id="integrations")
    
    response = demo_collection.insert_one(insert)
    print(response)
    insert = {"_id":"usecases", "tags":[
          "machine-learning",
          "building-sample-apps",
          "data-engineering",
          "event streaming",
          "game",
          "performance testing",
          "ds-bulk",
          "timeseries db",
          "devops",
          "continuous integration",
          "continuous deployment"
        ]   }
    response = demo_collection.insert_one(insert)
    print(response)
if __name__ == '__main__':
    main()
