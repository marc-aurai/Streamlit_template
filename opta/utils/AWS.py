import boto3
import json
from base64 import b64decode


def get_secret(secret_name: str, region: str) -> dict:
    """Lees een secret uit in AWS Secret manager, geef de secret name mee van de secret zoals het in AWS Secrets manager staat. 

    Args:
        secret_name (str): Secret name in AWS
        region (str): Standaard is dit gelijk aan Frankfurt, dus: "eu-central-1"

    Returns:
        dict: Secret 
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
    """Uploads een file naar de gewenste S3 bucket in AWS, indien je de rechten hebt. Enkel de EC2 instance (GPT-AI-Tool-ec2) heeft deze rechten momenteel.

    Args:
        file_name (str): De gewenste Naam van de file
        bucket (str): Naam van de S3 bucket waar je naar toe wilt uploaden
        object_name (str): De locatie van de file, waar het lokaal staat.

    Returns:
        Bool: True als het gelukt is met uploaden naar S3, anders False.
    """
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