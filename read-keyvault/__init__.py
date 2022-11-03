import logging
import os
import azure.functions as func
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    version = 'V18'

    try:
        keyVaultName = os.environ["KEY_VAULT_NAME"]
        KVUri = f"https://{keyVaultName}.vault.azure.net"

        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=KVUri, credential=credential)
        return func.HttpResponse(f"[{version}] the real secret of life: " + client.get_secret("supersecret").value)
    except Exception as e:
        return func.HttpResponse(f"[{version}] " + str(e) + f" | keyVaultName: {keyVaultName}")
