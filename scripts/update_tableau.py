"""
Script to push a CSV report to Tableau as a datasource.
"""

import os
import sys
import pandas as pd
import tableauserverclient as TSC
from tableauhyperapi import HyperProcess, Connection, SqlType, TableDefinition, Inserter, CreateMode, TableName, SchemaName, HyperException, Telemetry

TABLEAU_SERVER_URL = os.environ.get("TABLEAU_SERVER_URL")
TABLEAU_USERNAME = os.environ.get("TABLEAU_USERNAME")
TABLEAU_PASSWORD = os.environ.get("TABLEAU_PASSWORD")
TABLEAU_SITE = os.environ.get("TABLEAU_SITE", "")
TABLEAU_PROJECT = os.environ.get("TABLEAU_PROJECT")
TABLEAU_DATASOURCE_NAME = os.environ.get("TABLEAU_DATASOURCE_NAME")

INPUT_FILE = "member_report.csv"

def csv_to_hyper(csv_file, hyper_file):
    """Convert CSV file to Hyper format.
    
    Args:
        csv_file: Path to the input CSV file
        hyper_file: Path to the output Hyper file
    
    Returns:
        bool: True if conversion was successful, False otherwise
    """
    try:
        print(f"Converting CSV to Hyper format: {csv_file} -> {hyper_file}")
        
        df = pd.read_csv(csv_file)
        print(f"Loaded {len(df)} records from CSV")
        
        table_def = TableDefinition(
            table_name=TableName("Extract", "Extract"),
            columns=[
                TableDefinition.Column("login", SqlType.text()),
                TableDefinition.Column("email", SqlType.text()),
                TableDefinition.Column("last_activity_date", SqlType.text())
            ]
        )
        
        with HyperProcess(telemetry=Telemetry.SEND_USAGE_DATA_TO_TABLEAU) as hyper:
            with Connection(hyper.endpoint, hyper_file, CreateMode.CREATE_AND_REPLACE) as connection:
                connection.catalog.create_schema(SchemaName("Extract"))
                connection.catalog.create_table(table_def)
                
                with Inserter(connection, table_def) as inserter:
                    for _, row in df.iterrows():
                        inserter.add_row([
                            str(row["login"]),
                            str(row["email"]) if pd.notna(row["email"]) else "",
                            str(row["last_activity_date"]) if pd.notna(row["last_activity_date"]) else ""
                        ])
                    inserter.execute()
        
        print(f"Successfully converted CSV to Hyper format: {hyper_file}")
        return True
    
    except HyperException as e:
        print(f"Error converting CSV to Hyper: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error converting CSV to Hyper: {str(e)}")
        return False

def push_to_tableau():
    """Push the CSV data to Tableau as a datasource.
    
    Converts the CSV to Hyper format and then uses the Tableau Server Client
    Python library to publish the Hyper file as a datasource to a Tableau server.
    """
    if not all([TABLEAU_SERVER_URL, TABLEAU_USERNAME, TABLEAU_PASSWORD, 
                TABLEAU_PROJECT, TABLEAU_DATASOURCE_NAME]):
        print("Tableau configuration incomplete. Skipping Tableau upload.")
        return False
    
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Input file {INPUT_FILE} not found.")
        sys.exit(1)
    
    temp_hyper_file = "temp_tableau_upload.hyper"
    
    try:
        if not csv_to_hyper(INPUT_FILE, temp_hyper_file):
            print("Failed to convert CSV to Hyper format. Aborting upload.")
            return False
        
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
            
            print(f"Publishing Hyper datasource '{datasource.name}' to project '{project.name}'")
            
            datasource = server.datasources.publish(
                datasource,
                temp_hyper_file,
                TSC.Server.PublishMode.Overwrite
            )
            
            print(f"Successfully published datasource to Tableau: {datasource.name} (ID: {datasource.id})")
            return True
            
    except Exception as e:
        print(f"Error publishing to Tableau: {str(e)}")
        return False
    finally:
        if os.path.exists(temp_hyper_file):
            os.remove(temp_hyper_file)
            print(f"Removed temporary file: {temp_hyper_file}")

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
