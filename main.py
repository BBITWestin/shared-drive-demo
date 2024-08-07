from google_drive_handler import GoogleDriveHandler
from typing import List, Tuple
import os

DATA_FOLDER = os.path.expanduser("~/Desktop/peruse-demo-data")
os.makedirs(DATA_FOLDER, exist_ok=True)

try:
    file_handler = GoogleDriveHandler()
    files: List[Tuple[str, str]] = file_handler.list_csv_files()
    file_handler.load_csv_files(files, DATA_FOLDER)

except Exception as ex:
    print(ex)