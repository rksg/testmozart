from google.cloud import storage
from typing import Optional

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
