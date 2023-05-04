import boto3
import json
from base64 import b64decode
import pandas as pd

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


def read_S3_file(bucketName: str, fileName: str) -> pd.DataFrame:
    s3 = boto3.client('s3') 
    obj = s3.get_object(Bucket= bucketName, Key= fileName) 
    return pd.read_csv(obj['Body']) # 'Body' is a key word


def read_S3_club_logos(bucketName: str, fileName: str):
    print("read logo")
    s3 = boto3.client('s3') 
    obj = s3.get_object(Bucket= bucketName, Key= fileName) 
    return obj['Body'] # 'Body' is a key word