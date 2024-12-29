from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

from datetime import datetime
import io
import json

# Define the Google Drive API scope and parent folder ID
SCOPES = ['https://www.googleapis.com/auth/drive']
PARENT_FOLDER_ID = "1gfRT-mmYTpcP5wlAi06zSi7qdBdnUr-E"

# JSON string containing service account credentials
JSON_STRING = r'''{ 
  "type": "service_account",
  "project_id": "ai-assistant-competition",
  "private_key_id": "5b6454b9cfd0c6d7fba8c2b0239efd48f383b855",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC2AaJ3wELP7ZUY\necx9rYQX1qbX68zz0ahCllEMaBda+pubwyhj5AUkVQAr5b5q42m4c2zey6DM15kq\n7XEGijDgt+6/wium4B+94rlHLR+lM6LDgKLVdwanBDwbYz/sQvxcDCe5joLNYjQc\nq2phZYQq2jnzdpl7UyaNLsEOuWOkkwSsk818jwFLQBCYAiq1KsO5nj0koPSS2y9q\n73R7waMf+1A5QjNVZOQXblZX5ONWi6d7GwTeuWmqv+ZQJnURojU6cMv92IuKlDCS\nZQEl+wDK8msSERkh83tvEBxY9G12TBHccDLJ9p/KYu/l5WEtSLUAQXMCi6t9pZvu\nLMjcY8I9AgMBAAECggEAFROW4hmyUvxPA/TU1KfzkEQj8YSlqQV6H+3iyFZEgB1d\nyDmfE4Q8ATNTsAGsnZmkrD63mIxJnHcKDnHNISX/F4LNQ8kDP5GcM2POM1sbG0kh\nu9SJZsFgFJa1tDE33Y77RNiGgCMr7AdHhBtomAtGtSSsydAN4X1lTTuhESiwTIYk\nN/WTQcdHGFPrNm30nHof9xv0L86bs1f0U97pFK93ymTAamx/sKoscuJi/uSLqpFK\nDWrjr2F7Xhn5TWJ3LDfe03dqdkgJ5sP56xVV281xid8vBHDa/uxc4EZQxFMsPSMs\nF1wjogT1IZVp9sHbexrNUxuSLhuL65zXJWLPOBZNcQKBgQD++U+sTpMJDs8iv6zD\ne+qPu47oLZgmjLNBcx021edRHKwKTkO5EdPV09D/fUyhs54tdDadKH6j+q+Mh+t5\n25zFp4yluEuMUKZeAehwBrKlfe+UHEnXRzTd2V2ehMtgSYnwf8OdxKOW6hnHUFrL\nfGyzMjB8r4ydVEzOcR+95wKSEQKBgQC2vSXqViHsH25jryh6tutnKg62+QO+pwBd\nW1SxNc+ClUh7iY/xUtw3DXAxcbZeWvhzzgn8yhVn3jbo2BEiiUdSO4aa17G94r6Z\nnU36A/Dv8l/VeufaVInZRvXgyPjJkMsYZYvanOMkC7j4RjW7g5k2OA40DlgddkWt\nKEAZ2KGBbQKBgAjY2bze1RdBXkqUYAhAankmRuUjf94Gj8m7ls3qSiZ0WjvZT1xC\nlBkdSmkzDc+mjdyB5cs6Nnq2HhVAOhl2V1A8ahLt/CEYQ02Lv2bztIstfXykJqPD\nor/35Nm1PeFPa+veYwk8Y3i/ErnpvdzFqnflS+1nofdrj2ayYimStHIhAoGAbdzv\n85/PCy+mZWYENyrMAh0F9blmJ/QtQvNKyrOoS0DG8Aa3NIX1gV+h6QgNdVLJ9o2T\n8ZfpIKY3auuj+ZiA+Y5yEZvF73xnzOEG5V4DN68HMMiQpfGXYrrHzlnlQQG9KLC8\nUTVrVdt6XEGRwmeO8ErpNyC8lxHpN/5v81oLV00CgYBGMEjXtnCHuhKoD/MYzlcO\ncLv9JAbZx0Ea5hcKM3obS9oGghAQdRCdH4+9ybSqSaV3L7SkQiqimc+uw4OBfrD/\nNeLb6/P/1g2ct5i3dsidlBGD/TCKHUn/3FQblT1npPQ7mGvY1d1PeN4K5tYBn/lw\nVAWgD4FzC5dsaMZXhGnTPA==\n-----END PRIVATE KEY-----\n",
  "client_email": "autogen@ai-assistant-competition.iam.gserviceaccount.com",
  "client_id": "103055994633429436207",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/autogen%40ai-assistant-competition.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}'''
INFO = json.loads(JSON_STRING)

# Authenticates using service account credentials
def authenticate():
    creds = service_account.Credentials.from_service_account_info(INFO)
    return creds

# Uploads a string as a txt file to Google Drive
def upload_text_as_file(text_content, filename):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    
    # Encode text content as UTF-8
    file_stream = io.BytesIO(text_content.encode('utf-8'))  # Encode to UTF-8 to handle special characters
    media = MediaIoBaseUpload(file_stream, mimetype='text/plain')

    file_metadata = {
        'name': f"{filename}.txt",
        'parents': [PARENT_FOLDER_ID]
    }

    service.files().create(body=file_metadata, media_body=media, fields='id').execute()

# Returns the id of a file in Google Drive (if it exists), using its name 
def find_file_by_name(filename):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    
    results = service.files().list(
        q=f"name='{filename}' and '{PARENT_FOLDER_ID}' in parents and trashed=false",
        spaces='drive',
        fields='files(id, name)',
        pageSize=10
    ).execute()
    
    items = results.get('files', [])
    if not items:
        print(f'No files found with the name: {filename}')
        return None
    
    for item in items:
        if item['name'] == filename:
            return item['id']
    
    return None

# Reads the content of a file in Google Drive, using its id
def read_file_content(file_id):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    
    request = service.files().get_media(fileId=file_id)
    file_stream = io.BytesIO()
    downloader = MediaIoBaseDownload(file_stream, request)
    
    done = False
    while done is False:
        _,done = downloader.next_chunk()
    
    file_stream.seek(0)
    content = file_stream.read().decode('utf-8')
    return content

# Combines find_file_by_name and read_file_content in a single function
def get_text_from_file(filename_to_read):
    file_id_to_read = find_file_by_name(filename_to_read)
    if file_id_to_read:
        file_content = read_file_content(file_id_to_read)
        return file_content
    return None

# Finds a file in Google Drive by matching the user_id_game_id pattern, ignoring the timestamp.
def find_file_by_name_without_timestamp(base_filename):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    
    # Search for files in the parent folder with a name that starts with the base filename
    query = (
        f"name contains '{base_filename}' and "
        f"'{PARENT_FOLDER_ID}' in parents and "
        f"trashed=false"
    )
    
    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name)',
        pageSize=10
    ).execute()
    
    items = results.get('files', [])
    if not items:
        print(f"No files found with the pattern: {base_filename}")
        return None
    
    # Return matching files
    for item in items:
        if base_filename in item['name']:
            return item['id']

# Combines find_file_by_name (without timestamp) and read_file_content in a single function
def get_text_from_file_without_timestamp(filename_to_read):
    file_id_to_read = find_file_by_name_without_timestamp(filename_to_read)
    if file_id_to_read:
        file_content = read_file_content(file_id_to_read)
        return file_content
    return None

# Deletes a file in Google Drive using its ID
def delete_file_by_id(file_id):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)
    service.files().delete(fileId=file_id).execute()
    print(f"File with ID '{file_id}' deleted successfully.")

# Function to overwrite a file (check if exists, delete, then upload)
def overwrite_text_file(text_content, filename):
    # Extract base_filename (user_id_game_id) by removing the timestamp
    base_filename = "_".join(filename.split("_")[:-1])

    # Check if a file with the same name exists
    file_id_to_delete = find_file_by_name_without_timestamp(base_filename)
    
    if file_id_to_delete:
        # Delete the existing file
        delete_file_by_id(file_id_to_delete)
        print(f"Existing file '{base_filename}_..._.txt' deleted.")
    else:
        print(f"No existing file named '{filename}.txt' found.")
    
    # Upload the new file
    upload_text_as_file(text_content, filename)
    print(f"New file '{filename}.txt' uploaded successfully.")