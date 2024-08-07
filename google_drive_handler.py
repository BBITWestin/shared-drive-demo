# google_drive_handler.py

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from io import BytesIO
import time
import os
from typing import List, Tuple, Optional

# Path to the service account JSON file
SERVICE_ACCOUNT_FILE = "./service_account_secret.json"
# Scopes define the level of access requested
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

class GoogleDriveHandler:
    def __init__(self):
        """
        Initialize the GoogleDriveHandler with credentials and build the Drive service.
        """
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        self.service = build("drive", "v3", credentials=creds)

    def list_csv_files(self) -> List[Tuple[str, str]]:
        """
        List all CSV files in the shared drives.
        
        Returns:
            List[Tuple[str, str]]: A list of tuples containing file IDs and names.
        """
        print("\n--- STARTING GOOGLE DRIVE FILE SEARCH ---")
        shared_files = self.find_all_shared_drive_files(folder_id=None, folder_name=None)
        print(f"\n--- FOUND {len(shared_files)} FILES IN TOTAL ---")
        return shared_files
    
    def find_all_shared_drive_files(self, folder_id: Optional[str] = None, folder_name: Optional[str] = None) -> List[Tuple[str, str]]:
        """
        Recursively find all files in shared drives or a specific folder.
        
        Args:
            folder_id (Optional[str]): ID of the folder to search in. If None, search in "Shared with me".
            folder_name (Optional[str]): Name of the folder being searched. Used for logging.
        
        Returns:
            List[Tuple[str, str]]: A list of tuples containing file IDs and names.
        """
        print("--- SEARCHING SHARED WITH ME ---") if folder_id is None else print(f"--- SEARCHING FOUND: {folder_name} ---")

        shared_files = []
        query = "sharedWithMe=true" if folder_id is None else f"'{folder_id}' in parents"
        page_token = None

        while True:
            # Query the Drive API for files
            results = (self.service.files().list(
                q=query,
                fields="nextPageToken, files(id, name, mimeType, permissions)",
                pageToken=page_token
            ).execute())
            items = results.get("files", [])
            print(f"Found {len(items)} items in {'Shared with me' if folder_id is None else f'{folder_name} folder'}")

            for item in items:
                item_name = item["name"].lower()
                item_id = item["id"]
                mime_type = item["mimeType"]
                permissions = item.get("permissions", [])

                # Print item details
                print("\n", "NAME:", item_name, "\tID:", item_id, "\tTYPE:", folder_id, "\tFROM:", "Shared" if folder_name is None else folder_name)
                # for permission in permissions:
                #     print(permission.get("role", "N/A"), permission.get("emailAddress", "N/A"))

                # Handle Folders: recursively process the folder
                if mime_type == "application/vnd.google-apps.folder":
                    shared_files.extend(self.find_all_shared_drive_files(item_id, item_name))

                # Handle Files: add CSV files with specific naming pattern
                elif item_name.endswith("_lane_rate_data_report.csv"):
                    shared_files.append((item_id, item_name))

            # Check if there are more pages of results
            page_token = results.get("nextPageToken")
            if not page_token:
                break

        return shared_files
    
    def load_csv_files(self, csv_files, output_file_path: str):
        print("\n---Downloading Files---")

        for file_id, file_name in csv_files:
            # print(file_name, file_id)
            csv_content = self._load_csv(file_id, file_name)
            if csv_content:
                file_path = os.path.join(output_file_path, file_name)
                with open(file_path, "wb") as f:
                    f.write(csv_content)

    def _load_csv(self, file_id, file_name, max_retries=2):
        retry_count = 0
        csv_content = None

        while retry_count < max_retries:
            try:
                fh = BytesIO()
                request = self.service.files().get_media(fileId=file_id)
                downloader = MediaIoBaseDownload(fh, request) # chunksize=2048 * 2048
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    print(f"{file_name} ({file_id}) download: %d%% ..."% int(status.progress() * 100))
                csv_content = fh.getvalue()
                
                # Check if the file is empty
                if len(csv_content) == 0:
                    print(f"{file_name} ({file_id}) is empty. Skipping download.")
                    return None
                break
            except HttpError as error:
                retry_count += 1
                print(f"An error occurred while downloading {file_name} ({file_id}): {error}")
                time.sleep(1)

        return csv_content