import boto3
from datetime import datetime, timedelta, timezone
import pytz

def send_sns_notification(subject, message):
    sns_client = boto3.client('sns')
    sns_topic_arn = 'arn:aws:sns:us-east-1:654654326949:EIP'
    sns_client.publish(
        TopicArn=sns_topic_arn,
        Subject=subject,
        Message=message
    )

def get_bucket_creation_date(bucket_name):
    s3_client = boto3.client('s3')
    response = s3_client.get_bucket_location(Bucket=bucket_name)
    region = response.get('LocationConstraint', 'us-east-1') or 'us-east-1'
    return region

def utc_to_local(utc_dt, tz):
    local_tz = pytz.timezone(tz)
    local_dt = utc_dt.replace(tzinfo=timezone.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)

def check_s3_buckets():
    s3_client = boto3.client('s3')
    response = s3_client.list_buckets()
    s3_buckets_found = False
    s3_message_body = ""

    current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
    time_threshold = current_time - timedelta(days=1)

    for bucket in response['Buckets']:
        bucket_name = bucket['Name']
        creation_date_utc = bucket['CreationDate'].replace(tzinfo=timezone.utc)
        creation_date_ist = utc_to_local(creation_date_utc, 'Asia/Kolkata')
        region = get_bucket_creation_date(bucket_name)

        if region == 'ap-south-1':
            creation_date_ist = utc_to_local(creation_date_utc, 'Asia/Kolkata')

        if creation_date_utc > time_threshold:
            s3_buckets_found = True
            s3_message_body += f"S3 Bucket found:\n" \
                               f"Bucket Name: {bucket_name}\n" \
                               f"Creation Date (IST): {creation_date_ist}\n" \
                               f"Region: {region}\n\n"

            print(f"S3 Bucket found: {bucket_name}")

    if s3_buckets_found:
        s3_message_body += "Description: S3 Buckets Found"
        send_sns_notification("S3 Bucket Activity Detected", s3_message_body)
    else:
        print("No S3 Buckets found from last 24 hrs")

if __name__ == "__main__":
    check_s3_buckets()
