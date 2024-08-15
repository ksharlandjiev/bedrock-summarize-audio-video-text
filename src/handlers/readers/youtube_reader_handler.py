import os
from handlers.abstract_handler import AbstractHandler
from pytubefix import YouTube
import moviepy.editor as mp

class YouTubeReaderHandler(AbstractHandler):
    def handle(self, request: dict) -> dict:
        url = str(request.get("path"))
        print("Downloading YouTube video from: ", url)

        audio_file_path = self.download_youtube_video_audio(url, os.getenv('DIR_STORAGE'))        
        
        request.update({"path": audio_file_path})
        return super().handle(request)

    def download_youtube_video_audio(self, url, output_path="downloads"):
        """
        Downloads the audio from a YouTube video.
        """
        # Ensure output directory exists
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Download video from YouTube
        yt = YouTube(url)
        video = yt.streams.filter(only_audio=True).first()
        out_file = video.download(output_path)

        # Extract audio using moviepy (convert to mp3)
        base, ext = os.path.splitext(out_file)
        new_file = base + '.mp3'
        clip = mp.AudioFileClip(out_file)
        clip.write_audiofile(new_file)
        clip.close()

        # Remove the original download (mp4)
        os.remove(out_file)

        return new_file