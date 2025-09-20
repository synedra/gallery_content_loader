from __future__ import print_function
from github import Github
from dotenv import load_dotenv
import os.path
import os
import json
import re

load_dotenv()

from astrapy import DataAPIClient

# Use production setup - working configuration from test.py
client = DataAPIClient(os.environ['ASTRA_DB_APPLICATION_TOKEN'])
database = client.get_database_by_api_endpoint(
    "https://dea45ecb-38ea-4a45-8fb9-f0fb5e27dd91-us-east-2.apps.astra.datastax.com"
)

my_collection = database.get_collection('apps')
tag_collection = database.get_collection('tags')

# Initialize GitHub client
g = Github(os.environ["GITHUB_TOKEN"])

# Compile regex for tag validation
p = re.compile('[a-zA-Z]+')

# Organizations to scan
ORGANIZATIONS = ['DataStaxDevs', 'DataStax-Examples']


def get_astra_json_content(repo):
    """Get and parse astra.json content from a repository."""
    try:
        astrajson = repo.get_contents("astra.json")
        return json.loads(astrajson.decoded_content.decode())
    except Exception:
        return None


def create_base_entry(repo):
    """Create a base entry for a repository."""
    entry = {
        "name": repo.name,
        "description": repo.description or "",
        "urls": {
            "github": [repo.html_url]
        },
        "tags": [],
        "stack": [],
        "stargazers": repo.stargazers_count,
        "forks": repo.forks_count,
        "last_modified": repo.updated_at.isoformat(),
        "language": repo.language or ""
    }
    
    # Add language as a tag if it exists
    if repo.language:
        entry["tags"].append(repo.language.lower())
    
    return entry


def process_astra_json_settings(entry, settings):
    """Process astra.json settings and update entry accordingly."""
    for key, value in settings.items():
        key_upper = key.upper()
        
        if key_upper == "GITHUBURL":
            continue
        elif key_upper == "GITPODURL":
            entry["urls"]["gitpod"] = [value]
        elif key_upper == "NETLIFYURL":
            entry["urls"]["netlify"] = [value]
        elif key_upper == "DEMOURL":
            entry["urls"]["demo"] = [value]
        elif key_upper == "VERCELURL":
            entry["urls"]["vercel"] = [value]
        elif key_upper == "TAGS":
            process_tags(entry, value)
        elif key_upper == "STACK":
            process_stack(entry, value)
        else:
            entry[key.lower()] = value


def process_tags(entry, tags):
    """Process tags from astra.json and add to entry."""
    for tag in tags:
        if isinstance(tag, dict) and "name" in tag:
            tag_name = tag["name"]
        else:
            tag_name = str(tag)
        
        if p.match(tag_name) and tag_name.lower() not in entry["tags"]:
            entry["tags"].append(tag_name.lower())


def process_stack(entry, stack_items):
    """Process stack items from astra.json and add to entry."""
    for stack in stack_items:
        if not p.match(stack):
            continue
        
        stack_lower = stack.lower()
        if stack_lower not in entry["stack"]:
            entry["stack"].append(stack_lower)
        if stack_lower not in entry["tags"]:
            entry["tags"].append(stack_lower)


def process_repository(repo):
    """Process a single repository and return entry with astra.json data if available."""
    print(f"Processing repository: {repo.name}")
    
    # Check for astra.json file
    astra_settings = get_astra_json_content(repo)
    if not astra_settings:
        print(f"No astra.json found in {repo.name}, skipping...")
        return None
    
    print(f"Found astra.json in {repo.name}")
    
    # Create base entry
    entry = create_base_entry(repo)
    
    # Process astra.json settings
    process_astra_json_settings(entry, astra_settings)
    
    return entry


def collect_tag_counts(entries):
    """Collect tag counts from all entries."""
    tagdict = {}
    
    for entry in entries:
        # Count tags
        for tag in entry.get("tags", []):
            if tag:
                tagdict[tag.lower()] = tagdict.get(tag.lower(), 0) + 1
        
        # Count stack items
        for stack in entry.get("stack", []):
            if stack:
                tagdict[stack.lower()] = tagdict.get(stack.lower(), 0) + 1
    
    return tagdict


def save_entries_to_database(entries):
    """Save entries to the database."""
    print("Saving entries to database...")
    for entry in entries:
        try:
            my_collection.insert_one(entry)
            print(f"Saved {entry['name']} to database")
        except Exception as e:
            print(f"Error saving {entry['name']}: {e}")


def save_tags_to_database(tagdict):
    """Save tag counts to the database."""
    print("Saving tags to database...")
    for tag, count in tagdict.items():
        try:
            tag_collection.insert_one({'name': tag, 'count': count})
            print(f"Saved tag '{tag}' with count {count}")
        except Exception as e:
            print(f"Error saving tag '{tag}': {e}")


def main():
    """Scans GitHub repositories for DataStax organizations and processes their data."""
    print("Starting GitHub repository scan...")
    entries = []
    
    # Scan each organization
    for org_name in ORGANIZATIONS:
        print(f"Processing organization: {org_name}")
        try:
            organization = g.get_organization(org_name)
            for repo in organization.get_repos():
                entry = process_repository(repo)
                if entry:
                    entries.append(entry)
                    
        except Exception as e:
            print(f"Error processing organization {org_name}: {e}")
            continue
    
    print(f"Found {len(entries)} repositories with astra.json files")
    
    # Collect tag counts
    tagdict = collect_tag_counts(entries)
    
    # Save to database
    save_entries_to_database(entries)
    save_tags_to_database(tagdict)
    
    print(f"Processing complete! Processed {len(entries)} repositories and {len(tagdict)} unique tags.")


if __name__ == '__main__':
    main()
