import os

from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential

endpoint = os.getenv("COSMOS_ENDPOINT")
database_name = os.getenv("COSMOS_DATABASE", "codeflux")
container_name = os.getenv("COSMOS_CONTAINER", "contacts")

credential = DefaultAzureCredential()

client = CosmosClient(
    endpoint,
    credential=credential,
)

database = client.get_database_client(database_name)
container = database.get_container_client(container_name)

def save_contact(contact: dict):
    return container.create_item(body=contact)