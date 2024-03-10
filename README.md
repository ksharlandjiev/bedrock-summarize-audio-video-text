# Amazon Bedrock Chat & Summarization Tool

This project automates the transcription and summarization of audio, video, and text content using AWS services. By leveraging Amazon Transcribe for speech-to-text conversion, Amazon Textract for OCR of printed or handwritten text and Amazon Bedrock for generating summaries using foundational GenAI models, the tool streamlines the analysis of multimedia and textual information. Additionally, it supports text anonymization, and other handy features such as reading from HTTP(s) URL or PDF text extraction.

## NOTICE

- **Demonstration Purposes**: This code is intended for **demonstration purposes ONLY**. It will incur AWS charges based on the usage of Amazon Textract, Amazon Transcribe, Amazon Bedrock, and Amazon S3 services. 

**Please review AWS pricing details for each service used** 

## Architectural Overview

The application employs the Chain of Responsibility design pattern to process inputs through a series of handlers. Each handler in the chain is responsible for a specific type of task, such as downloading YouTube videos, transcribing audio, summarizing text, or handling files from local file system or Amazon S3. This pattern provides flexibility in processing and allows for easy customization of the processing pipeline. It has been enhanced with dynamic handler discovery using Factory pattern to automatically identify and instantiate handlers as needed, significantly simplifying the extension and customization of the processing pipeline.


### AWS Services Used

- **Amazon Transcribe**: Converts spoken words in audio or video files into text, producing accurate transcriptions.
- **Amazon Textract**: Automatically extract printed text, handwriting, layout elements, and data from any document.
- **Amazon Bedrock**: Employs advanced AI models to summarize text, making it easier to digest large volumes of information.
- **Amazon S3**: Acts as a storage solution for the input files and the generated outputs, including transcripts and summaries.
- **Others** - Such as Quip for example.


### Chain of Responsibility Implementation
The processing chain is composed of several handlers, that are dedicated to a particular processing step and organized into 3 groups: readers, processors, writers:

Readers:
- **LocalFileReaderHandler**: Handles local audio, video, and text files for processing.
- **S3ReaderHandler**: Manages the reading and downloading of S3 objects (files) from Amazon S3.
- **PDFReaderHandler**: Extracts text from PDF documents for summarization.
= **HTTPHandler**: Generic HTTP handler that allows you to fetch HTML data from http(s) endpoints. It uses BeautifulSoup to clean HTML tags. 
- **YouTubeReaderHandler**: Downloads videos from YouTube URLs and extracts audio.

Processors:
- **AmazonBedrockHandler**: Summarizes text content using Amazon Bedrock.
- **AmazonTranscriptionHandler**: Transcribes audio files into text using Amazon Transcribe.
- **AmazonTextractHandler**: Extracts text from images such as .jpg, .png, .tiff
- **AnonymizeHandler**: Configurable via .env - will use SpaCy library to anonymize customer names. 
- **PromptHandler**: Uses a minimalistic prompt framework - all your prompts can be stored in the prompts/ folder and you can select which prompt to use when invoking the main.py.

Writers:
- **S3WriterHandler**: Manages the uploading of of S3 objects (files) to Amazon S3.
-**LocalFileWriterHandler**: Writes output into a local file.
-**ClipboardWriterHandler**: Writes output into clipboard.


Handlers are linked together in a chain, where each handler passes its output to the next handler in the sequence until the processing is complete.

### Customizing the Processing Chain
You can customize the processing chain in main.py by setting the sequence of handlers according to your specific needs. Here is an example of how to construct a custom processing chain:
```python
from handlers.handler_factory import HandlerFactory

def construct_chain():
    youtube_handler =  HandlerFactory.get_handler("YouTubeReaderHandler")
    amazon_s3_writer_handler =  HandlerFactory.get_handler("AmazonS3WriterHandler")
    amazon_transcribe_handler =  HandlerFactory.get_handler("AmazonTranscriptionHandler")
    amazon_bedrock_handler =  HandlerFactory.get_handler("AmazonBedrockHandler")
    anonymize_handler =  HandlerFactory.get_handler("AnonymizeHandler")
    prompt_handler =  HandlerFactory.get_handler("PromptHandler")

    # Read Youtube Video >> Save Audio in Amazon S3 >> Extract text from speach (Amazon Transcribe) >> Construct a prompt >> Summarize using Amazon Bedrock.
    youtube_handler.set_next(amazon_s3_writer_handler).set_next(amazon_transcribe_handler).set_next(prompt_handler).set_next(anonymize_handler).set_next(amazon_bedrock_handler)

    request = {"path": "https://www.youtube.com/watch?v=tQi97_DWi6A", "prompt_file_name": "default_prompt"}
    youtube_handler.handle(request)
```

With the introduction of dynamic handler discovery and command-line arguments, you can now easily customize or specify custom processing chains without altering the codebase. The CLI supports flags for using predefined or custom chains based on runtime arguments.




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
2. **Install [ffmpeg](https://www.ffmpeg.org/download.html)**

3. **Create a `.env` file** at the root of your project directory.
4. **Add your AWS S3 configuration** to the `.env` file:

```bash
# .env file
# AWS Specific configuration
BEDROCK_ASSUME_ROLE=None
AWS_DEFAULT_REGION="us-east-1"

# Amazon S3 bucket used for Amazon transcribe
BUCKET_NAME=your-s3-bucket-name
S3_FOLDER=uploads/
OUTPUT_FOLDER=transcriptions/

# Amazon Bedrock Settings
AMAZON_BEDROCK_MODEL_ID="anthropic.claude-3-sonnet-20240229-v1:0"
AMAZON_BEDROCK_MODEL_PROPS='{"max_tokens":4096, "anthropic_version": "bedrock-2023-05-31", "messages": [{"role": "user", "content": ""}]}'
AMAZON_BEDROCK_PROMPT_TEMPLATE="{prompt_text}"
AMAZON_BEDROCK_PROMPT_INPUT_VAR="$.messages[0].content"
AMAZON_BEDROCK_OUTPUT_JSONPATH="$.content[0].text"

# AMAZON_BEDROCK_MODEL_ID="anthropic.claude-v2"
# AMAZON_BEDROCK_MODEL_PROPS='{"prompt": "", "max_tokens_to_sample":4096, "temperature":0.5, "top_k":250, "top_p":0.5, "stop_sequences":[] }'
# AMAZON_BEDROCK_PROMPT_TEMPLATE="\n\nHuman:{prompt_text}\n\nAssistant:"
# AMAZON_BEDROCK_PROMPT_INPUT_VAR="$.prompt"
# AMAZON_BEDROCK_OUTPUT_JSONPATH="$.completion"

# AMAZON_BEDROCK_MODEL_ID="amazon.titan-text-express-v1"
# AMAZON_BEDROCK_MODEL_PROPS='{"inputText": "", "textGenerationConfig":{ "maxTokenCount":4096, "stopSequences":[], "temperature":0, "topP":1 }}'
# AMAZON_BEDROCK_PROMPT_TEMPLATE="\n{prompt_text}"
# AMAZON_BEDROCK_PROMPT_INPUT_VAR="$.inputText"
# AMAZON_BEDROCK_OUTPUT_JSONPATH="$.results[0].outputText"

# Copy output to clipboard
CLIPBOARD_COPY=false

# For Anonymization
ANONYMIZE_CUSTOMER_NAME_REPLACEMENT="[Customer]"

# Local download folder
DIR_STORAGE="downloads"

# Used for integration with Quip
QUIP_TOKEN="<your_personal_token>"
QUIP_ENDPOINT="https://platform.quip.com"
QUIP_DEFAULT_FOLDER_ID=<default_folder_for_writing>
```
### Usage

Execute the `main.py` script, specifying the file path and an optional prompt template name:
```bash
python src/main.py <path_to_file_or_url> [prompt_file_name] [--chat {sum_first,chat_first,chat_only}] [--anonymize {yes}] [--custom] 
```

- `<path_to_file_or_youtube_url>`: The path to your audio or video file.
- `[prompt_file_name]`: Optional. The name of a custom prompt template (without the `.txt` extension). 
- `--chat`: Enable interactive chat option. You can choose if you want to have a chat before or after summarization task, or chat only.
- `--anonymize`: way to turn off anonymization. Currently this is enabled by default. 
- `--custom`: Allows you to execute a custom chain, defined in src/main.py: construct_custom_chain()

Example: 
* Processing an Audio File
```bash
python src/main.py /path/to/file.mp3
```

* Using a cutom prompt template, located in `prompts/my_custom_prompto.txt`
```bash
python src/main.py /path/to/file.pdf my_custom_prompt

```
* Executing with a custom processing chain:
```bash
python src/main.py /path/to/file.mp3 --custom

```
* Have a conversation with the LLM about your document
```bash
python src/main.py /path/to/local/file.pdf --chat=chat_only
```

## Acknowledgments

This project takes inspiration from the **Amazon Bedrock Workshop**, provided by AWS Samples. The workshop offers a comprehensive guide and tools for integrating Amazon Bedrock into applications, which have been instrumental in developing the summarization functionalities of this project. For more information and access to these resources, visit the [Amazon Bedrock Workshop on GitHub](https://github.com/aws-samples/amazon-bedrock-workshop).

## NOTICE

- **AWS CLI Installation**: Ensure the AWS CLI is installed and configured with your AWS credentials.
- **Demonstration Purposes**: This code is intended for **demonstration purposes ONLY**. It will incur AWS charges based on the usage of Amazon Transcribe, Amazon Bedrock, and Amazon S3 services. 
** Please review AWS pricing details for each service used** 
- **Use at Your Own Risk**: The author assumes no liability for any charges or consequences arising from the use of this tool.

## Contributing

Contributions are welcome! Please feel free to fork the repository, make changes, and submit pull requests.

## License

This project is released under the MIT License.




