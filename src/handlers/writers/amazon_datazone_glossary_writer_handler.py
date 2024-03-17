import json
from typing import Any, Dict
from handlers.abstract_handler import AbstractHandler
from utils.aws_boto_client_manager import AWSBotoClientManager
from botocore.exceptions import ClientError

class AmazonDataZoneGlossaryWriterHandler(AbstractHandler):

    def handle(self, request: dict) -> dict:
        self.datazone_client = AWSBotoClientManager.get_client('datazone')

        print("Processing DataZone glossaries...")

        if not self.validate_glossary_structure(request.get("text")):
            raise ValueError("The glossary structure is invalid.")

        domain_id = request.get("domain_id") or input("Enter the DataZone Domain ID: ")
        project_id = request.get("project_id") or input("Enter the DataZone Project ID: ")
        
        self.process_glossary(request["text"], domain_id, project_id)

        return super().handle(request)

    def validate_glossary_structure(self, glossary_text: str) -> bool:
        try:
            glossary = json.loads(glossary_text)
            return isinstance(glossary, dict) and all(
                isinstance(terms, list) and all(
                    isinstance(term, dict) and "name" in term and "shortDescription" in term for term in terms
                ) for category, terms in glossary.items()
            )
        except json.JSONDecodeError:
            return False

    def process_glossary(self, glossary_text: str, domain_id: str, project_id: str):
        glossary = json.loads(glossary_text)
        for category, terms in glossary.items():
            glossary_id = self.create_or_get_glossary(category, domain_id, project_id)
            for term in terms:
                self.add_term_to_glossary(domain_id, glossary_id, term)

    def create_or_get_glossary(self, category_name: str, domain_id: str, project_id: str) -> str:
        try:
            # Search for an existing glossary using the Search API
            response = self.datazone_client.search(
                domainIdentifier=domain_id,
                owningProjectIdentifier=project_id,
                searchScope='GLOSSARY',
                searchText=category_name,
                maxResults=1,
                filters={
                    'filter': {
                        'attribute': 'name',
                        'value': category_name
                    }
                }
            )
            # Check if the glossary exists
            if response['totalMatchCount'] > 0:
                glossary_id = response['items'][0]['glossaryItem']['id']
                print(f"Found existing glossary for: {category_name} with ID: {glossary_id}")
                return glossary_id
        except ClientError as error:
            print(f"Error searching for glossary: {error}")
            raise

        # If no existing glossary found, or searching failed, create a new one
        print(f"Creating new glossary for: {category_name}")
        try:
            create_response = self.datazone_client.create_glossary(
                domainIdentifier=domain_id,
                owningProjectIdentifier=project_id,
                name=category_name,
                description=f"Glossary for {category_name}",
                status='ENABLED',
            )
            return create_response["id"]
        except ClientError as error:
            print(f"Error creating glossary: {error}")
            raise

    def add_term_to_glossary(self, domain_id, glossary_id: str, term: Dict[str, Any]):
        try:
            self.datazone_client.create_glossary_term(
                domainIdentifier=domain_id,
                glossaryIdentifier=glossary_id,
                name=term['name'],
                shortDescription=term['shortDescription'],
                status='ENABLED'            
            )
        except ClientError as error:
            print(f"Error adding term '{term['name']}' to glossary: {error}")
