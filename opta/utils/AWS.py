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
            return json.loads(secret)
        secret = b64decode(response["SecretBinary"])
        return json.loads(secret)


def data_to_S3(file_name: str, bucket: str, object_name: str):
    if object_name is None:
        object_name = file_name
    s3 = boto3.client('s3')
    try:
        response = s3.upload_file(file_name, bucket, Key=object_name)
    except:
        print(response.get("ResponseMetadata", {}).get("HTTPStatusCode"))
        return False
    print('Successfully uploaded dataset: {}'.format(file_name))
    return True