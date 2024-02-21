# AWS Audio/Video Summarization Tool

This project automates the transcription of audio and video files and their subsequent summarization, leveraging the power of Amazon Web Services (AWS). It utilizes Amazon Transcribe for speech-to-text conversion, Amazon Bedrock for text summarization, and Amazon S3 for storing both the input files and the resulting outputs. A unique feature of this tool is its prompt template system, which allows for customizable summarization prompts based on user requirements.

## Description

This tool simplifies the process of extracting insights from transcripts, audio and video content. By automating transcription and summarization, it facilitates quick understanding and analysis of multimedia information.

### AWS Services Used

- **Amazon Transcribe**: Converts spoken words in audio or video files into text, producing accurate transcriptions.
- **Amazon Bedrock**: Employs advanced AI models to summarize text, making it easier to digest large volumes of information.
- **Amazon S3**: Acts as a storage solution for the input files and the generated outputs, including transcripts and summaries.

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
BUCKET_NAME=your-s3-bucket-name
S3_FOLDER=uploads/
OUTPUT_FOLDER=transcriptions/
```


### Usage

Execute the `main.py` script, specifying the file path and an optional prompt template name:
```bash
python src/main.py path/to/your/file.mp3 [custom_prompt]
```

- `path/to/your/file.mp3`: The path to your audio or video file.
- `[custom_prompt]`: Optional. The name of a custom prompt template (without the `.txt` extension).

## Acknowledgments

This project utilizes utility tooling from the **Amazon Bedrock Workshop**, provided by AWS Samples. The workshop offers a comprehensive guide and tools for integrating Amazon Bedrock into applications, which have been instrumental in developing the summarization functionalities of this project. For more information and access to these resources, visit the [Amazon Bedrock Workshop on GitHub](https://github.com/aws-samples/amazon-bedrock-workshop).

## NOTICE

- **AWS CLI Installation**: Ensure the AWS CLI is installed and configured with your AWS credentials.
- **Demonstration Purposes**: This code is intended for demonstration and may incur AWS charges based on the usage of Amazon Transcribe, Amazon Bedrock, and Amazon S3 services. 
** Please review AWS pricing details for each service used.** 

- **Use at Your Own Risk**: The author assumes no liability for any charges or consequences arising from the use of this tool.

## Contributing

Contributions are welcome! Please feel free to fork the repository, make changes, and submit pull requests.

## License

This project is released under the MIT License.




