import boto3
from botocore.exceptions import ClientError
import logging

# Настройка логгера
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def add_tags_to_bucket(bucket_name, new_tags):
    s3_client = boto3.client('s3')

    try:
        existing_tags = s3_client.get_bucket_tagging(Bucket=bucket_name).get('TagSet', [])
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchTagSet':
            existing_tags = []
        else:
            logger.error(f"Error getting bucket tagging: {e}")
            raise

    updated_tags = existing_tags + new_tags
    updated_tags_set = {tuple(tag.items()) for tag in updated_tags}
    updated_tags = [dict(tag) for tag in updated_tags_set]

    try:
        s3_client.put_bucket_tagging(
            Bucket=bucket_name,
            Tagging={'TagSet': updated_tags}
        )
        print(f"added tags to bucket: {bucket_name}")
    except ClientError as e:
        logger.error(f"Error putting bucket tagging: {e}")
        raise

def lambda_handler(event, context):
    s3_client = boto3.client('s3')
    print(event)
    try:
        response = s3_client.list_buckets()
        buckets = response['Buckets']
    except ClientError as e:
        logger.error(f"Error listing buckets: {e}")
        raise

    for bucket in buckets:
        bucket_name = bucket['Name']
        default_tags = [{'Key': 'BucketName', 'Value': bucket_name}]

        try:
            existing_tags = s3_client.get_bucket_tagging(Bucket=bucket_name).get('TagSet', [])
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchTagSet':
                existing_tags = []
            else:
                logger.error(f"Error getting bucket tagging: {e}")
                raise

        new_tags = [tag for tag in default_tags if tag not in existing_tags]

        if new_tags:
            add_tags_to_bucket(bucket_name, new_tags)

    # Пример логирования
    logger.info("Теги успешно добавлены к ведрам.")
    return {"statusCode": 200, "body": "Теги успешно добавлены к ведрам."}
