# src/summarization.py
import json
import sys, os
from utils import bedrock

def summarize_text_with_bedrock(prompt_text, modelId='anthropic.claude-v2'):
    """
    Summarizes the given text using Amazon Bedrock, based on a prompt specified by prompt_file_name.
    """    
    module_path = "."
    sys.path.append(os.path.abspath(module_path))
    
    try:
        boto3_bedrock = bedrock.get_bedrock_client( assumed_role=os.environ.get("BEDROCK_ASSUME_ROLE", None), region=os.environ.get("AWS_DEFAULT_REGION", None))
    except (BotoCoreError, ClientError) as e:
        print(f"Failed to create Bedrock client: {e}")
        return

    prompt = f""""

Human:"{prompt_text}"

Assistant:"
    """

    
    body = json.dumps({"prompt": prompt,
              "max_tokens_to_sample":4096,
              "temperature":0.5,
              "top_k":250,
              "top_p":0.5,
              "stop_sequences":[]
              }) 

    try:
        accept = 'application/json'
        contentType = 'application/json'
        
        response = boto3_bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
        response_body = json.loads(response.get('body').read())

        return response_body.get('completion')
        
    except (BotoCoreError, ClientError) as e:
        print(f"Failed to invoke model: {e}")
