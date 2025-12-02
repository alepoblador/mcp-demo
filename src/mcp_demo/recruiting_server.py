import httpx
import sheets

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from mcp.server.fastmcp import FastMCP
from pydantic import Field
from typing import Annotated

APPLICATION_FORM_ID = "1Th8hR3NpCPR0L49De2swsRRbFjX8mhOKiF9ecwoQ_hU"
APPLICANT_NAME_QUESTION_ID = "11b4fc09"
EMAIL_QUESTION_ID = "641a1b43"
MOTIVATION_QUESTION_ID = "355c31ed"
EXPERIENCE_QUESTION_ID = "589509d8"

TRACKING_SHEET_ID = "1-bxa6-T6lwLxMl8_iKSQCAxp0cVqaBuxoxUKqPINkL4"
SHEET_NAME = "Applications"

JOB_DESCRIPTION_FILE_PATH = "resources/job_description.txt"
EMAIL_TEMPLATE_INVITE_FILE_PATH = "resources/email_template_invite.txt"
EMAIL_TEMPLATE_REJECT_FILE_PATH = "resources/email_template_reject.txt"
EMAIL_TEMPLATE_FOLLOW_UP_FILE_PATH = "resources/email_template_follow_up.txt"

SCOPES = [
    'https://www.googleapis.com/auth/forms.responses.readonly',
    'https://www.googleapis.com/auth/spreadsheets'
]

credentials = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)

# Google services
forms_service = build('forms', 'v1', credentials=credentials)
sheets_service = build('sheets', 'v4', credentials=credentials)

mcp = FastMCP("recruiting_assistant", log_level="ERROR")

async def fetch_form_responses():
    request = forms_service.forms().responses().list(formId=APPLICATION_FORM_ID)
    responses = request.execute().get('responses', [])

    return [
        {
            'application_id': response['responseId'],
            'applicant_name': response['answers'][APPLICANT_NAME_QUESTION_ID]['textAnswers']['answers'][0]['value'],
            'email': response['answers'][EMAIL_QUESTION_ID]['textAnswers']['answers'][0]['value'],
            'motivation': response['answers'][MOTIVATION_QUESTION_ID]['textAnswers']['answers'][0]['value'],
            'experience': response['answers'][EXPERIENCE_QUESTION_ID]['textAnswers']['answers'][0]['value'],
        } 
        for response in responses
    ]

@mcp.tool(
    name="fetch_new_applications",
    description="Fetch new applications from Google Forms.",
)
async def fetch_new_applications():
    responses = await fetch_form_responses()
    if not responses:
        return "No new applications found."
    
    # Process and return the responses
    return {"applications": responses}

@mcp.tool(
    name="update_tracker",
    description="Update a given application's data in the Google Sheet tracker.",
)
async def update_tracker(
    application: Annotated[
        dict[str, str],
        Field(description="The application data including application_id, applicant_name, email, motivation, experience")
    ],
):
    result = sheets.upsert_row(
        sheets_service,
        TRACKING_SHEET_ID,
        SHEET_NAME,
        application
    )

    if not result:
        return "Failed to update tracker."
    
    return {"status": "Tracker updated successfully."}

@mcp.resource("resource://job_description")
async def job_description():
    return open(JOB_DESCRIPTION_FILE_PATH).read()

@mcp.resource("resource://email_template_invite")
async def email_template_invite():
    return open(EMAIL_TEMPLATE_INVITE_FILE_PATH).read()

@mcp.resource("resource://email_template_reject")
async def email_template_reject():
    return open(EMAIL_TEMPLATE_REJECT_FILE_PATH).read()

@mcp.resource("resource://email_template_follow_up")
async def email_template_follow_up():
    return open(EMAIL_TEMPLATE_FOLLOW_UP_FILE_PATH).read()

@mcp.prompt(name="evaluate_application")
def evaluate_application() -> str:
    """Evaluates an application based on the job description."""
    return f"""
    You are a recruiter.
    Your goal is to evaluate the application data against the provided job requirements and e-mail templates.
    --- TASK ---
    1. Calculate a compatibility score (1-5, 5 being best).
    2. Determine the recommendation (Pass, Reject).
    3. Write a 1-sentence summary justifying your decision.
    4. If the recommendation is Pass, draft an interview invitation email using the invite email template.
    If the recommendation is Reject, draft a rejection email using the reject template.
    5. Call the update_tracker tool to update the application record. To do this, return
    a JSON object with the following keys:
        - application_id: str
        - applicant_name: str
        - email: str
        - motivation: str
        - experience: str
        - initial_evaluation: str (Pass or Reject)
    """

def main():
    # Initialize and run the server
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()

