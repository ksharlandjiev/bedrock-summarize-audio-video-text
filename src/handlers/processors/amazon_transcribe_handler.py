import os
import time
import json
from handlers.abstract_handler import AbstractHandler
from utils.aws_boto_client_manager import AWSBotoClientManager
class AmazonTranscriptionHandler(AbstractHandler):

    def handle(self, request: dict) -> dict:
        s3_file_path = request.get("path")

        print("Starting Amazon Transcribe job for: ", s3_file_path)
        transcript = self.extract_transcript(s3_file_path)

        # updating the request body and adding the transcribed text.
        request.update({"text": transcript})

        return super().handle(request)

    def extract_transcript(self, s3_file_path):
        """
        Orchestrates the transcription process for audio/video files, including summarization.
        """

        # Accessing variables from .env file
        BUCKET_NAME = os.getenv('BUCKET_NAME')
        OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER')

        # Start the transcription job
        job_name, transcribe_client = self.start_transcribe_job(s3_file_path, BUCKET_NAME, OUTPUT_FOLDER)
        
        # Wait for the job to complete
        job_status = self.wait_for_job_completion(transcribe_client, job_name)
        
        if job_status['TranscriptionJob']['TranscriptionJobStatus'] == 'COMPLETED':
            # Fetch the transcript
            transcript = self.fetch_transcript(BUCKET_NAME, job_name, OUTPUT_FOLDER)
            
            # Delete the transcription job to clean up
            self.delete_transcription_job(transcribe_client, job_name)

            return transcript
        else:
            print(f"Transcription job {job_name} failed.")

    def start_transcribe_job(self, s3_file_path, bucket_name, output_folder):
        """
        Starts an Amazon Transcribe job for the specified file.
        """
        transcribe_client = AWSBotoClientManager.get_client('transcribe')
        
        job_name = f"transcription_{int(time.time())}"
        media_uri = s3_file_path
        media_format = s3_file_path.split('.')[-1]
        
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': media_uri},
            MediaFormat=media_format,
            LanguageCode='en-US',
            OutputBucketName=bucket_name,
            OutputKey=output_folder,
            Settings={'ShowSpeakerLabels': True, 'MaxSpeakerLabels': 2}
        )
        return job_name, transcribe_client


    def wait_for_job_completion(self, transcribe_client, job_name):
        """
        Waits for the transcription job to complete and returns the job status.
        """
        while True:
            status = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
            if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                return status
            time.sleep(30)

    def fetch_transcript(self, BUCKET_NAME, job_name, OUTPUT_FOLDER):
        """
        Fetches the transcript result from the S3 bucket.
        """
        s3_client = AWSBotoClientManager.get_client('s3')
        transcript_file_key = f"{OUTPUT_FOLDER}{job_name}.json"
        result = s3_client.get_object(Bucket=BUCKET_NAME, Key=transcript_file_key)
        transcript = json.loads(result["Body"].read().decode("utf-8"))
        return transcript['results']['transcripts'][0]['transcript']

    def delete_transcription_job(self, transcribe_client, job_name):
        """
        Deletes the specified transcription job.
        """
        transcribe_client.delete_transcription_job(TranscriptionJobName=job_name)