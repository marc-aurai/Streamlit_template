import boto3
import json
from base64 import b64decode

def get_secret(secret_name: str, region: str) -> dict:
        """
        Reads secret from secrets manager.
        """
        # Create a Secrets Manager client
        session = boto3.session.Session()
        client = session.client(service_name="secretsmanager", region_name=region)
        response = client.get_secret_value(SecretId=secret_name)
        if "SecretString" in response:
            secret = response["SecretString"]
            print(type(secret), secret.keys())
            return json.loads(secret)
        secret = b64decode(response["SecretBinary"])
        print(type(secret), secret.keys())
        return json.loads(secret)