import streamlit as st
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload

from datetime import datetime
import io
import json

# Define the Google Drive API scope and parent folder ID
SCOPES = ['https://www.googleapis.com/auth/drive']
PARENT_FOLDER_ID = st.secrets["folder_id"]

# JSON string containing service account credentials
JSON_STRING = st.secrets["drive"]
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
def overwrite_text_file(text_content, filename, remove_timestamp=True):
    
    if remove_timestamp == True:
        # Extract base_filename (user_id_game_id) by removing the timestamp
        base_filename = "_".join(filename.split("_")[:-1])

        # Check if a file with the same name exists
        file_id_to_delete = find_file_by_name_without_timestamp(base_filename)
    
    elif remove_timestamp == False:
        file_id_to_delete = find_file_by_name(filename)
        filename = filename.split('.txt')[0]

    if file_id_to_delete:
        # Delete the existing file
        delete_file_by_id(file_id_to_delete)
    
    # Upload the new file
    upload_text_as_file(text_content, filename)
    print(f"New file '{filename}.txt' uploaded successfully.")

# Function to find and delete a file
def find_and_delete(filename):
    file_id_to_delete = find_file_by_name(filename)
    if file_id_to_delete:
        delete_file_by_id(file_id_to_delete)