import os
import json
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests
from pytube import YouTube
from handlers.abstract_handler import AbstractHandler
from utils.web_utils import fetch_webpage

class HTTPHandler(AbstractHandler):

    def handle(self, request: dict) -> dict:
        url = request.get("path", None)
        print("Fetching data from web page:", url)
        response = fetch_webpage(url)
        
        if response:
            soup = BeautifulSoup(response, 'html.parser')
            text_content = soup.get_text(separator='\n')
            media_files = []
            
            # Determine the write file path and output folder
            write_file_path = request.get("write_file_path", None)
            if write_file_path:
                base_folder = os.path.dirname(write_file_path)
                file_id = os.path.basename(write_file_path).split('.')[0]
                output_folder = os.path.join(base_folder, file_id)
                media_folder = os.path.join(output_folder, "media")
                os.makedirs(media_folder, exist_ok=True)
            
            # Initialize the metadata dictionary
            if "metadata" not in request:
                request["metadata"] = {}
            
            # Extract media if required
            if request.get("extract_media", False):
                # Extract images
                for img in soup.find_all('img'):
                    img_url = img.get('src')
                    if img_url:
                        img_data = self.fetch_media(img_url)
                        if img_data:
                            img_name = os.path.basename(urlparse(img_url).path)
                            img_path = os.path.join(media_folder, img_name)
                            with open(img_path, 'wb') as f:
                                f.write(img_data)
                            media_files.append({"type": "image", "path": img_path, "source_url": img_url})
                
                # Extract videos
                for video in soup.find_all('video'):
                    video_url = video.get('src')
                    if video_url:
                        video_data = self.fetch_media(video_url)
                        if video_data:
                            video_name = os.path.basename(urlparse(video_url).path)
                            video_path = os.path.join(media_folder, video_name)
                            with open(video_path, 'wb') as f:
                                f.write(video_data)
                            media_files.append({"type": "video", "path": video_path, "source_url": video_url})

                # Extract audios
                for audio in soup.find_all('audio'):
                    audio_url = audio.get('src')
                    if audio_url:
                        audio_data = self.fetch_media(audio_url)
                        if audio_data:
                            audio_name = os.path.basename(urlparse(audio_url).path)
                            audio_path = os.path.join(media_folder, audio_name)
                            with open(audio_path, 'wb') as f:
                                f.write(audio_data)
                            media_files.append({"type": "audio", "path": audio_path, "source_url": audio_url})

                # Extract YouTube videos
                for iframe in soup.find_all('iframe'):
                    src = iframe.get('src')
                    if 'youtu' in src:
                        youtube_url = src if 'youtube.com' in src else 'https://www.youtube.com/embed/' + src.split('/')[-1]
                        video_path = self.download_youtube_video(youtube_url, media_folder)
                        if video_path:
                            media_files.append({"type": "video", "path": video_path, "source_url": youtube_url})

            # Save the transcript to a text file
            transcript_file_path = os.path.join(output_folder, 'transcript.txt')
            with open(transcript_file_path, 'w') as transcript_file:
                transcript_file.write(text_content)
            
            # Create metadata with traceability for graph database
            metadata = {
                "original_url": url,
                "transcript_file": transcript_file_path,
                "media_files": media_files
            }
            
            # Save metadata to a json file
            metadata_file_path = os.path.join(output_folder, 'metadata.json')
            with open(metadata_file_path, 'w') as metadata_file:
                json.dump(metadata, metadata_file, indent=4)
            
            # Update the request metadata with the new metadata
            request["metadata"][url] = metadata

            # Update the request with the extracted text
            request.update({"text": text_content})
            
            print("Web page content and media fetched successfully.")
        else:
            print("Failed to fetch web page content.")
        
        return super().handle(request)
    
    def fetch_media(self, media_url):
        try:
            response = requests.get(media_url, stream=True)
            if response.status_code == 200:
                return response.content
            else:
                print(f"Failed to fetch media: {media_url}")
                return None
        except Exception as e:
            print(f"Error fetching media: {e}")
            return None
    
    def download_youtube_video(self, url, output_path="downloads"):
        """
        Downloads the video from a YouTube link.
        """
        try:
            # Ensure output directory exists
            if not os.path.exists(output_path):
                os.makedirs(output_path)

            # Download video from YouTube
            yt = YouTube(url)
            video = yt.streams.filter(progressive=True, file_extension='mp4').first()
            out_file = video.download(output_path)

            return out_file
        except Exception as e:
            print(f"Error downloading YouTube video: {e}")
            return None
