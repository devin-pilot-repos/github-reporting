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
- GitHub account ID
- Login (username)
- Email address (if public)
- Full name (if available)
- Date of last activity
- Account creation date
- Account last update date
- Account type
- Company (if provided)
- Location (if provided)

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

To test the script locally:

1. Clone this repository
2. Install dependencies: `pip install requests pandas tableauserverclient`
3. Set the required environment variables
4. Run the script: `python scripts/generate_member_report.py`

## License

This project is licensed under the MIT License - see the LICENSE file for details.
