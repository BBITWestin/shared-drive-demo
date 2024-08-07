# Google Drive CSV File Downloader Demo

This demo downloads CSV files from a shared Google Drive folder using a Google
Service Account.

## Prerequisites

- Google Service Account with Drive access

## Setup

1. Clone this repo

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Place your `service_account_secret.json` in the project root. It should look
   something like this:

```json
{
  "type": "service_account",
  "project_id": "",
  "private_key_id": "",
  "private_key": "-----BEGIN PRIVATE KEY-----\n.........\n-----END PRIVATE KEY-----\n",
  "client_email": "",
  "client_id": "",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "",
  "universe_domain": "googleapis.com"
}
```

## Google Drive Setup

1. Create a folder in Google Drive.

2. Share the folder with the service account email (found in
   `service_account_secret.json`).

3. Upload test files to the shared folder.

## Running the Demo

1. Navigate to the root of the project.

2. Run: `py main.py`

3. CSV files will be downloaded to `~/Desktop/peruse-demo-data`.

## Viewing Files Without Downloading

If you want to view the available files without downloading them, comment out
the following line in `main.py`:

```python
file_handler.load_csv_files(files, DATA_FOLDER)
```
