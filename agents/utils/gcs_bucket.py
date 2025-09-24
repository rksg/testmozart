from google.cloud import storage
from typing import Optional
import os
import tempfile

def upload_to_gcs(bucket_name: str, source_file_path: str, destination_blob_name: str, credentials_path: Optional[str] = None) -> None:
	"""
	Uploads a file to the specified GCS bucket.
	Args:
		bucket_name: Name of the GCS bucket.
		source_file_path: Local path to the file to upload.
		destination_blob_name: Destination path in the bucket.
		credentials_path: Optional path to GCP service account credentials JSON.
	"""
	if credentials_path:
		client = storage.Client.from_service_account_json(credentials_path)
	else:
		client = storage.Client()
	bucket = client.bucket(bucket_name)
	blob = bucket.blob(destination_blob_name)
	blob.upload_from_filename(source_file_path)

def download_from_gcs(bucket_name: str, source_blob_name: str, destination_file_path: str, credentials_path: Optional[str] = None) -> None:
	"""
	Downloads a file from the specified GCS bucket.
	Args:
		bucket_name: Name of the GCS bucket.
		source_blob_name: Path to the file in the bucket.
		destination_file_path: Local path to save the downloaded file.
		credentials_path: Optional path to GCP service account credentials JSON.
	"""
	if credentials_path:
		client = storage.Client.from_service_account_json(credentials_path)
	else:
		client = storage.Client()
	bucket = client.bucket(bucket_name)
	blob = bucket.blob(source_blob_name)
	blob.download_to_filename(destination_file_path)

def read_gcs_blob_as_text(bucket_name: str, blob_name: str, credentials_path: Optional[str] = None) -> str:
	"""
	Reads a text file from GCS and returns its contents as a string.
	Args:
		bucket_name: Name of the GCS bucket.
		blob_name: Path to the file in the bucket.
		credentials_path: Optional path to GCP service account credentials JSON.
	Returns:
		The contents of the file as a string.
	"""
	if credentials_path:
		client = storage.Client.from_service_account_json(credentials_path)
	else:
		client = storage.Client()
	bucket = client.bucket(bucket_name)
	blob = bucket.blob(blob_name)
	return blob.download_as_text()

def get_file_from_gcs(gcs_uri:str, credentials_path: Optional[str] = None) -> list[str]:
    """
    Retrieves the content of a file from GCS and save to local tempdir
    
    Args:
        gcs_uri: The GCS URI of the file to retrieve (e.g., gs://bucket_name/blob_name).
        blob_name: Path to the file in the bucket.
        credentials_path: Optional path to GCP service account credentials JSON.
    """
    if not gcs_uri.startswith('gs://'):
        raise ValueError("Invalid GCS URI format. Must start with gs://")
    # Remove 'gs://' prefix and split
    gcs_parts = gcs_uri[5:].split('/', 1)
    bucket_name = gcs_parts[0]
    if len(gcs_parts) > 1:
        blob_name = gcs_parts[1]
    else:
        raise ValueError("GCS URI must include a blob name after the bucket name.")
    repo_full = f"{bucket_name}/{blob_name}"
    local_path = os.path.join(tempfile.gettempdir(), repo_full)
    if not os.path.exists(local_path):
        download_from_gcs(bucket_name, blob_name, local_path, credentials_path)
    return [local_path]
