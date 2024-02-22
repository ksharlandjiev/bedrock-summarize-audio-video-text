# Amazon Bedrock Summarization Tool

This project automates the transcription and summarization of audio, video, and text content using AWS services. By leveraging Amazon Transcribe for speech-to-text conversion and Amazon Bedrock for generating summaries using foundational GenAI models, the tool streamlines the analysis of multimedia and textual information. Additionally, it supports downloading content from YouTube for processing and can handle PDF text extraction.

## NOTICE

- **Demonstration Purposes**: This code is intended for **demonstration purposes ONLY**. It will incur AWS charges based on the usage of Amazon Transcribe, Amazon Bedrock, and Amazon S3 services. 

**Please review AWS pricing details for each service used** 

## Architectural Overview

The application employs the Chain of Responsibility design pattern to process inputs through a series of handlers. Each handler in the chain is responsible for a specific type of task, such as downloading YouTube videos, transcribing audio, summarizing text, or handling files from local file system or Amazon S3. This pattern provides flexibility in processing and allows for easy customization of the processing pipeline.

### AWS Services Used

- **Amazon Transcribe**: Converts spoken words in audio or video files into text, producing accurate transcriptions.
- **Amazon Bedrock**: Employs advanced AI models to summarize text, making it easier to digest large volumes of information.
- **Amazon S3**: Acts as a storage solution for the input files and the generated outputs, including transcripts and summaries.


### Chain of Responsibility Implementation
The processing chain is composed of several handlers, each dedicated to a particular processing step:

- **YouTubeHandler**: Downloads videos from YouTube URLs and extracts audio.
- **S3WriterHandler**: Manages the uploading and downloading of files to and from Amazon S3.
- **S3ReaderHandler**: Manages the uploading and downloading of files to and from Amazon S3.
- **TranscriptionHandler**: Transcribes audio files into text using Amazon Transcribe.
- **PDFHandler**: Extracts text from PDF documents for summarization.
- **LocalFileHandler**: Handles local audio, video, and text files for processing.
- **SummarizationHandler**: Summarizes text content using Amazon Bedrock.
- **AnonymizeHandler**: Configurable via .env - will use SpaCy library to anonymize customer names. 
- **PromptHandler**: uses a minimalistic prompt framework - all your prompts can be stored in the prompts/ folder and you can select which prompt to use when invoking the main.py.
- **HTTPHandler**: Generic HTTP handler that allows you to fetch HTML data from http(s) endpoints. It uses BeautifulSoup to clean HTML tags.

Handlers are linked together in a chain, where each handler passes its output to the next handler in the sequence until the processing is complete.

### Customizing the Processing Chain
You can customize the processing chain in main.py by setting the sequence of handlers according to your specific needs. Here is an example of how to construct a custom processing chain:
```python
from handlers import YouTubeHandler, S3WriterHandler, TranscriptionHandler, SummarizationHandler

def construct_chain():
    youtube_handler = YouTubeHandler()
    s3writer_handler = S3WriterHandler()
    transcription_handler = TranscriptionHandler()    
    summarization_handler = SummarizationHandler()
    anonymize_handler = AnonymizeHandler()

    # Customize the chain of handlers
    youtube_handler.set_next(s3writer_handler).set_next(transcription_handler).set_next(prompt_handler).set_next(bedrock_handler)

    request = {"type": input_type, "path": file_path, "prompt_file_name": prompt_file_name}
    youtube_handler.handle(request)
```

### Prompt Template System

The tool features a prompt template system in the `prompts` folder, enabling users to tailor the summarization process. This system supports the use of custom prompts that can be specified at runtime, offering flexibility in how the summaries are generated.

## Getting Started

### Prerequisites

- Python 3.8+
- AWS CLI installed and configured with AWS credentials
- An active AWS account

### Installation

1. **Clone the repository:**
2. **Navigate to the project directory:**
3. **Install the required dependencies:**
```bash 
pip install -r requirements.txt
```

### Configuration
1. **Installing spaCy and Language Models** Download the English language model (or any model you prefer):**
```bash
python -m spacy download en_core_web_sm
```
2. **Create a `.env` file** at the root of your project directory.
3. **Add your AWS S3 configuration** to the `.env` file:

```bash
# AWS Specific configuration
BEDROCK_ASSUME_ROLE=None
AWS_DEFAULT_REGION="us-east-1"

# Amazon S3 bucket used for Amazon transcribe
BUCKET_NAME=your-s3-bucket-name
S3_FOLDER=uploads/
OUTPUT_FOLDER=transcriptions/
# Amazon Bedrock Settings
AMAZON_BEDROCK_MODEL_ID="anthropic.claude-v2"
# Copy output to clipboard
CLIPBOARD_COPY=false
# Use Anonymization
ANONYMIZE=false
ANONYMIZE_CUSTOMER_NAME_REPLACEMENT="[Customer]"
```
### Usage

Execute the `main.py` script, specifying the file path and an optional prompt template name:
```bash
python src/main.py <path_to_file_or_youtube_url> [prompt_file_name]
```

- `<path_to_file_or_youtube_url>`: The path to your audio or video file.
- `[prompt_file_name]`: Optional. The name of a custom prompt template (without the `.txt` extension). 
Example: 
```bash
python src/main.py path/to/your/file.mp3 summarize_audio
```
A prompt from `prompts/summarize_audio.txt` will be used.

## Acknowledgments

This project utilizes utility tooling from the **Amazon Bedrock Workshop**, provided by AWS Samples. The workshop offers a comprehensive guide and tools for integrating Amazon Bedrock into applications, which have been instrumental in developing the summarization functionalities of this project. For more information and access to these resources, visit the [Amazon Bedrock Workshop on GitHub](https://github.com/aws-samples/amazon-bedrock-workshop).

## NOTICE

- **AWS CLI Installation**: Ensure the AWS CLI is installed and configured with your AWS credentials.
- **Demonstration Purposes**: This code is intended for **demonstration purposes ONLY**. It will incur AWS charges based on the usage of Amazon Transcribe, Amazon Bedrock, and Amazon S3 services. 
** Please review AWS pricing details for each service used** 
- **Use at Your Own Risk**: The author assumes no liability for any charges or consequences arising from the use of this tool.

## Contributing

Contributions are welcome! Please feel free to fork the repository, make changes, and submit pull requests.

## License

This project is released under the MIT License.




