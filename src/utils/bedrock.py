# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# Python Built-Ins:
import json
import os
from jsonpath_ng import jsonpath, parse

# External Dependencies:
import boto3
from botocore.client import Config

def invoke_model(prompt_text, modelId=os.environ.get("AMAZON_BEDROCK_MODEL_ID", 'anthropic.claude-v2')):
    """
    Summarizes the given text using Amazon Bedrock, based on a prompt specified by prompt_file_name.
    """        

    try:
        # boto3_bedrock = bedrock.get_bedrock_client( assumed_role=os.environ.get("BEDROCK_ASSUME_ROLE", None), region=os.environ.get("AWS_DEFAULT_REGION", None))
        config = Config(connect_timeout=900)
        boto3_bedrock = boto3.client(service_name="bedrock-runtime", region_name=os.environ.get("AWS_DEFAULT_REGION", 'us-east-1'), config=config)

    except e:
        print(f"Failed to create Bedrock client: {e}")
        raise e
    
    body = json.loads(os.environ.get("AMAZON_BEDROCK_MODEL_PROPS", {"max_tokens_to_sample":4096, "temperature":0.5, "top_k":250, "top_p":0.5, "stop_sequences":[] }))
    prompt_template = os.environ.get("AMAZON_BEDROCK_PROMPT_TEMPLATE", None)
    prompt_var = os.environ.get("AMAZON_BEDROCK_PROMPT_INPUT_VAR", "prompt")
    output_json_path = os.environ.get("AMAZON_BEDROCK_OUTPUT_JSONPATH", "$")
    
    # Format the prompt.
    prompt_template = prompt_template.format(prompt_text=prompt_text) 

    # JSONPath expression
    jsonpath_expr = parse(prompt_var)
    # Find the path and set the new content
    for match in jsonpath_expr.find(body):
        # Check if the matched element is not at the root level
        if hasattr(match.full_path, 'left'):
            parent_path = match.full_path.left
            jsonpath_expr_update = parse(str(parent_path))
            for match_update in jsonpath_expr_update.find(body):
                match_update.value['content'] = prompt_template
        else: 
            # Directly modify the root element's value
            body[ str(match.full_path) ] = prompt_template
    
    body = json.dumps(body)
    try:
        accept = 'application/json'
        contentType = 'application/json'
        
        response = boto3_bedrock.invoke_model(body=body, modelId=modelId, accept=accept, contentType=contentType)
        response_body = json.loads(response.get('body').read())

        # Trying to fetch data from the response body based on pre-configured JSONPath expression
        jsonpath_expression = parse(output_json_path)        
        try: 
            result = jsonpath_expression.find(response_body)
        
            if result[0].value: 
                return result[0].value
        except: 
            print(f"Failed to apply JSONPAth: {output_json_path}, returning the whole body")
            return response_body
        
    except Exception as e:
        print(f"Failed to invoke model: {e}")
        raise e
