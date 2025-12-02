# Dev Notes:

- Using Claude Code extension for VS Code
- `src/mcp_demo/recruiting_server.py` is an MCP server which assists in receiving applications, evaluating them, keeping track, and responding to applicants
- It integrates with Google Forms API and Google Sheets API

- Tools

  - `fetch_new_applications`
    - fetches applications from Google Forms
  - `update_tracker`
    - updates a tracker spreadsheet in Google Sheets

- Resources

  - Job Description
  - Email templates for invite and reject

- Prompts
  - `evaluate_application`
    - provides detailed instructions about how to evaluate applications, draft emails using templates, and update the tracker
