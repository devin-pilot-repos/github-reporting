"""
Script to generate a CSV report of GitHub organization members and push to Tableau.
"""

import os
import sys
import csv
import json
import datetime
import requests
import pandas as pd
import tableauserverclient as TSC

GITHUB_API_URL = "https://api.github.com"
GITHUB_ORG = "devin-pilot-repos"
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")

TABLEAU_SERVER_URL = os.environ.get("TABLEAU_SERVER_URL")
TABLEAU_USERNAME = os.environ.get("TABLEAU_USERNAME")
TABLEAU_PASSWORD = os.environ.get("TABLEAU_PASSWORD")
TABLEAU_SITE = os.environ.get("TABLEAU_SITE", "")
TABLEAU_PROJECT = os.environ.get("TABLEAU_PROJECT")
TABLEAU_DATASOURCE_NAME = os.environ.get("TABLEAU_DATASOURCE_NAME")

OUTPUT_FILE = "member_report.csv"

def get_github_headers():
    """Return headers for GitHub API requests."""
    return {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

def get_org_members():
    """Get all members of the organization."""
    members_url = f"{GITHUB_API_URL}/orgs/{GITHUB_ORG}/members"
    members = []
    page = 1
    
    while True:
        response = requests.get(
            f"{members_url}?page={page}&per_page=100",
            headers=get_github_headers()
        )
        
        if response.status_code != 200:
            print(f"Error fetching members: {response.status_code}")
            print(response.text)
            sys.exit(1)
            
        page_members = response.json()
        if not page_members:
            break
            
        members.extend(page_members)
        page += 1
    
    return members

def get_user_details(username):
    """Get detailed information about a user."""
    user_url = f"{GITHUB_API_URL}/users/{username}"
    response = requests.get(user_url, headers=get_github_headers())
    
    if response.status_code != 200:
        print(f"Error fetching user details for {username}: {response.status_code}")
        return None
        
    return response.json()

def get_user_events(username):
    """Get recent events for a user to determine last activity."""
    events_url = f"{GITHUB_API_URL}/users/{username}/events"
    response = requests.get(
        f"{events_url}?per_page=1",
        headers=get_github_headers()
    )
    
    if response.status_code != 200:
        print(f"Error fetching events for {username}: {response.status_code}")
        return None
        
    events = response.json()
    if events:
        return events[0].get("created_at")
    return None

def generate_csv_report():
    """Generate CSV report with member information."""
    members = get_org_members()
    report_data = []
    
    print(f"Found {len(members)} members in the organization")
    
    for member in members:
        username = member.get("login")
        user_details = get_user_details(username)
        last_activity = get_user_events(username)
        
        if user_details:
            report_data.append({
                "login": username,
                "email": user_details.get("email", ""),
                "last_activity_date": last_activity or ""
            })
    
    with open(OUTPUT_FILE, "w", newline="") as csvfile:
        fieldnames = ["login", "email", "last_activity_date"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(report_data)
    
    print(f"CSV report generated: {OUTPUT_FILE}")
    return report_data

def push_to_tableau(data):
    """Push the CSV data to Tableau as a datasource."""
    if not all([TABLEAU_SERVER_URL, TABLEAU_USERNAME, TABLEAU_PASSWORD, 
                TABLEAU_PROJECT, TABLEAU_DATASOURCE_NAME]):
        print("Tableau configuration incomplete. Skipping Tableau upload.")
        return False
    
    try:
        tableau_auth = TSC.TableauAuth(TABLEAU_USERNAME, TABLEAU_PASSWORD, TABLEAU_SITE)
        server = TSC.Server(TABLEAU_SERVER_URL)
        
        with server.auth.sign_in(tableau_auth):
            all_projects, pagination_item = server.projects.get()
            project = next((p for p in all_projects if p.name == TABLEAU_PROJECT), None)
            
            if not project:
                print(f"Project '{TABLEAU_PROJECT}' not found")
                return False
            
            datasource = TSC.DatasourceItem(project.id)
            datasource.name = TABLEAU_DATASOURCE_NAME
            
            df = pd.DataFrame(data)
            
            temp_file = "temp_tableau_upload.csv"
            df.to_csv(temp_file, index=False)
            
            datasource = server.datasources.publish(
                datasource,
                temp_file,
                TSC.Server.PublishMode.Overwrite
            )
            
            os.remove(temp_file)
            
            print(f"Successfully published datasource to Tableau: {datasource.name}")
            return True
            
    except Exception as e:
        print(f"Error publishing to Tableau: {str(e)}")
        return False

def main():
    """Main function to generate report and push to Tableau."""
    if not GITHUB_TOKEN:
        print("GITHUB_TOKEN environment variable is required")
        sys.exit(1)
    
    data = generate_csv_report()
    
    if any([TABLEAU_SERVER_URL, TABLEAU_USERNAME, TABLEAU_PASSWORD]):
        push_to_tableau(data)

if __name__ == "__main__":
    main()
