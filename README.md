# GitHub Organization Reporting

This repository contains GitHub Actions workflows for generating reports about the [devin-pilot-repos](https://github.com/devin-pilot-repos) organization.

## Member Report Workflow

The Member Report workflow queries all active members in the devin-pilot-repos organization, creates a CSV report with their GitHub account IDs, emails, and dates of last activity, and pushes this data as a datasource into a Tableau dashboard.

### Workflow Schedule

The workflow runs:
- Daily at midnight UTC
- Manually via workflow dispatch

### Generated Report

The CSV report includes the following information for each organization member:
- Login (username)
- Email address (if public)
- Date of last activity

### Tableau Integration

The workflow pushes the generated CSV as a datasource to a Tableau dashboard. This requires the following secrets to be configured in the repository:

- `TABLEAU_SERVER_URL`: URL of the Tableau server
- `TABLEAU_USERNAME`: Tableau username
- `TABLEAU_PASSWORD`: Tableau password
- `TABLEAU_SITE`: Tableau site name (optional)
- `TABLEAU_PROJECT`: Tableau project name
- `TABLEAU_DATASOURCE_NAME`: Name for the datasource in Tableau

### GitHub Authentication

The workflow uses the built-in `GITHUB_TOKEN` to authenticate with the GitHub API. This token has read-only access to organization data.

## Development

### Prerequisites

- Python 3.10+
- Required Python packages: `requests`, `pandas`, `tableauserverclient`

### Local Testing

It's recommended to use a virtual environment for local testing to isolate dependencies.

#### Setting Up a Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install common dependencies
pip install requests pandas tableauserverclient
```

#### Testing CSV Generation

To test the CSV generation script locally:

1. Clone this repository
2. Set up and activate a virtual environment as shown above
3. Install required dependencies:
   ```bash
   pip install requests pandas
   ```
4. Set the required environment variables:
   ```bash
   # On Windows (PowerShell):
   $env:GITHUB_TOKEN="your_github_token"  # or ORG_ACCESS_TOKEN
   
   # On macOS/Linux:
   export GITHUB_TOKEN=your_github_token  # or ORG_ACCESS_TOKEN
   ```
5. Run the script: `python scripts/generate_csv_report.py`
6. When finished, deactivate the virtual environment: `deactivate`

#### Testing Tableau Integration

To test the Tableau integration script locally:

1. First generate a CSV report using the steps above or create a sample CSV with the following columns:
   ```csv
   login,email,last_activity_date
   user1,user1@example.com,2025-05-01T12:00:00Z
   user2,user2@example.com,2025-05-02T12:00:00Z
   ```

2. Set up and activate a virtual environment as shown above

3. Install required dependencies:
   ```bash
   pip install pandas tableauserverclient
   ```

4. Set the required environment variables:
   ```bash
   # On Windows (PowerShell):
   $env:TABLEAU_SERVER_URL="https://your-tableau-server.com"
   $env:TABLEAU_USERNAME="your_username"
   $env:TABLEAU_PASSWORD="your_password"
   $env:TABLEAU_SITE="your_site"  # Optional
   $env:TABLEAU_PROJECT="your_project"
   $env:TABLEAU_DATASOURCE_NAME="github_members"
   
   # On macOS/Linux:
   export TABLEAU_SERVER_URL=https://your-tableau-server.com
   export TABLEAU_USERNAME=your_username
   export TABLEAU_PASSWORD=your_password
   export TABLEAU_SITE=your_site  # Optional
   export TABLEAU_PROJECT=your_project
   export TABLEAU_DATASOURCE_NAME=github_members
   ```

5. Run the script: `python scripts/update_tableau.py`

6. When finished, deactivate the virtual environment: `deactivate`

7. Troubleshooting:
   - Ensure your Tableau server is accessible from your local machine
   - Verify your credentials have permission to publish datasources
   - Check that the specified project exists in your Tableau site
   - If you encounter SSL errors, you may need to set `export PYTHONHTTPSVERIFY=0` (not recommended for production)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
