"""
Script to push a CSV report to Tableau as a datasource.
"""

import os
import sys
import pandas as pd
import tableauserverclient as TSC

TABLEAU_SERVER_URL = os.environ.get("TABLEAU_SERVER_URL")
TABLEAU_USERNAME = os.environ.get("TABLEAU_USERNAME")
TABLEAU_PASSWORD = os.environ.get("TABLEAU_PASSWORD")
TABLEAU_SITE = os.environ.get("TABLEAU_SITE", "")
TABLEAU_PROJECT = os.environ.get("TABLEAU_PROJECT")
TABLEAU_DATASOURCE_NAME = os.environ.get("TABLEAU_DATASOURCE_NAME")

INPUT_FILE = "member_report.csv"

def push_to_tableau():
    """Push the CSV data to Tableau as a datasource.
    
    Uses the Tableau Server Client Python library to publish a CSV file
    as a datasource to a Tableau server.
    """
    if not all([TABLEAU_SERVER_URL, TABLEAU_USERNAME, TABLEAU_PASSWORD, 
                TABLEAU_PROJECT, TABLEAU_DATASOURCE_NAME]):
        print("Tableau configuration incomplete. Skipping Tableau upload.")
        return False
    
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file {INPUT_FILE} not found.")
        sys.exit(1)
    
    try:
        print(f"Loading CSV file: {INPUT_FILE}")
        df = pd.read_csv(INPUT_FILE)
        print(f"Loaded {len(df)} records from CSV")
        
        temp_file = "temp_tableau_upload.csv"
        df.to_csv(temp_file, index=False)
        
        print(f"Connecting to Tableau server: {TABLEAU_SERVER_URL}")
        tableau_auth = TSC.TableauAuth(TABLEAU_USERNAME, TABLEAU_PASSWORD, TABLEAU_SITE)
        server = TSC.Server(TABLEAU_SERVER_URL)
        
        with server.auth.sign_in(tableau_auth):
            print("Successfully authenticated with Tableau Server")
            
            all_projects, pagination_item = server.projects.get()
            project = next((p for p in all_projects if p.name == TABLEAU_PROJECT), None)
            
            if not project:
                print(f"Project '{TABLEAU_PROJECT}' not found")
                return False
            
            print(f"Found project: {project.name} (ID: {project.id})")
            
            datasource = TSC.DatasourceItem(project.id)
            datasource.name = TABLEAU_DATASOURCE_NAME
            
            print(f"Publishing CSV datasource '{datasource.name}' to project '{project.name}'")
            
            datasource = server.datasources.publish(
                datasource,
                temp_file,
                TSC.Server.PublishMode.Overwrite
            )
            
            print(f"Successfully published datasource to Tableau: {datasource.name} (ID: {datasource.id})")
            return True
            
    except Exception as e:
        print(f"Error publishing to Tableau: {str(e)}")
        return False
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
            print(f"Removed temporary file: {temp_file}")

def main():
    """Main function to push CSV to Tableau."""
    if not all([TABLEAU_SERVER_URL, TABLEAU_USERNAME, TABLEAU_PASSWORD]):
        print("Tableau configuration incomplete. Required environment variables:")
        print("  - TABLEAU_SERVER_URL")
        print("  - TABLEAU_USERNAME")
        print("  - TABLEAU_PASSWORD")
        print("  - TABLEAU_PROJECT")
        print("  - TABLEAU_DATASOURCE_NAME")
        sys.exit(1)
    
    success = push_to_tableau()
    
    if success:
        print("Successfully updated Tableau datasource")
    else:
        print("Failed to update Tableau datasource")
        sys.exit(1)

if __name__ == "__main__":
    main()
