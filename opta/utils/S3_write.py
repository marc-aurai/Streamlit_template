import boto3

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