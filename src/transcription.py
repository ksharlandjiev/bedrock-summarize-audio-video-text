# src/transcription.py
import boto3
import time
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Accessing variables from .env file
BUCKET_NAME = os.getenv('BUCKET_NAME')
S3_FOLDER = os.getenv('S3_FOLDER')
OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER')

def upload_file_to_s3(file_path, BUCKET_NAME, S3_FOLDER):
    """
    Uploads a file to an S3 bucket and returns the S3 path.
    """
    s3_client = boto3.client('s3')
    file_name = file_path.split('/')[-1]
    s3_path = f"{S3_FOLDER}{file_name}"
    s3_client.upload_file(file_path, BUCKET_NAME, s3_path)
    return s3_path

def start_transcribe_job(s3_file_path, BUCKET_NAME, OUTPUT_FOLDER):
    """
    Starts an Amazon Transcribe job for the specified file.
    """
    transcribe_client = boto3.client('transcribe')
    job_name = f"transcription_{int(time.time())}"
    media_uri = f"s3://{BUCKET_NAME}/{s3_file_path}"
    media_format = s3_file_path.split('.')[-1]
    
    transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': media_uri},
        MediaFormat=media_format,
        LanguageCode='en-US',
        OutputBucketName=BUCKET_NAME,
        OutputKey=OUTPUT_FOLDER,
        Settings={'ShowSpeakerLabels': True, 'MaxSpeakerLabels': 2}
    )
    return job_name, transcribe_client

def wait_for_job_completion(transcribe_client, job_name):
    """
    Waits for the transcription job to complete and returns the job status.
    """
    while True:
        status = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
        if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
            return status
        time.sleep(30)

def fetch_transcript(BUCKET_NAME, job_name, OUTPUT_FOLDER):
    """
    Fetches the transcript result from the S3 bucket.
    """
    s3_client = boto3.client('s3')
    transcript_file_key = f"{OUTPUT_FOLDER}{job_name}.json"
    result = s3_client.get_object(Bucket=BUCKET_NAME, Key=transcript_file_key)
    transcript = json.loads(result["Body"].read().decode("utf-8"))
    return transcript['results']['transcripts'][0]['transcript']

def delete_transcription_job(transcribe_client, job_name):
    """
    Deletes the specified transcription job.
    """
    transcribe_client.delete_transcription_job(TranscriptionJobName=job_name)

def extract_transcript(file_path, prompt_file_name):
    """
    Orchestrates the transcription process for audio/video files, including summarization.
    """
    
    # Upload the file to S3
    s3_file_path = upload_file_to_s3(file_path, BUCKET_NAME, S3_FOLDER)
    
    # Start the transcription job
    job_name, transcribe_client = start_transcribe_job(s3_file_path, BUCKET_NAME, OUTPUT_FOLDER)
    
    # Wait for the job to complete
    job_status = wait_for_job_completion(transcribe_client, job_name)
    
    if job_status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
        # Fetch the transcript
        transcript = fetch_transcript(BUCKET_NAME, job_name, OUTPUT_FOLDER)
        
        # Delete the transcription job to clean up
        delete_transcription_job(transcribe_client, job_name)

        return transcript
    else:
        print(f"Transcription job {job_name} failed.")
