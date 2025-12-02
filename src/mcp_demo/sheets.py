def get_all_rows(sheets_service, sheet_id: str, sheet_name: str):
    """
    Retrieve all rows from the specified Google Sheet.
    """
    range_name = f"'{sheet_name}'!A1:H"  # Assuming 5 columns: ID, Name, Email, Motivation, Experience
    request = sheets_service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=range_name
    )
    response = request.execute()
    return response.get('values', [])  # Returns list of rows

def update_row(sheets_service, sheet_id: str, sheet_name: str, row_index: int, row_data: list):
    """
    Update a specific row in the Google Sheet.
    """
    range_name = f"'{sheet_name}'!A{row_index + 1}:H"
    body = {'values': [row_data]}
    
    request = sheets_service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=range_name,
        valueInputOption='USER_ENTERED',
        body=body
    )
    result = request.execute()
    return result

def add_new_row(sheets_service, sheet_id: str, sheet_name: str, row_data: list):
    """
    Append a new row to the bottom of the sheet.
    """
    range_name = f"'{sheet_name}'!A:A"  # Append to end
    body = {'values': [row_data]}
    
    request = sheets_service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range=range_name,
        valueInputOption='USER_ENTERED',
        body=body
    )
    result = request.execute()
    return result

def upsert_row(sheets_service, sheet_id: str, sheet_name: str, application: dict[str, str]):
    """
    Insert or update a row based on a unique identifier.
    """
    rows = get_all_rows(sheets_service, sheet_id, sheet_name)

    application_id = application['application_id']
    row_data = [
        application['application_id'],
        application['applicant_name'],
        application['email'],
        application['motivation'],
        application['experience'],
        application.get('initial_evaluation', '')
    ]
    
    for index, row in enumerate(rows):
        if row and row[0] == application_id:  # Assuming the unique ID is in the first column
            return update_row(sheets_service, sheet_id, sheet_name, index, row_data)
    
    return add_new_row(sheets_service, sheet_id, sheet_name, row_data)