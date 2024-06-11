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

def list_buckets_created_last_24_hours():
    s3_client = boto3.client('s3')
    response = s3_client.list_buckets()

    current_time = datetime.utcnow().replace(tzinfo=timezone.utc)
    time_threshold = current_time - timedelta(days=1)

    buckets_to_delete = []

    for bucket in response['Buckets']:
        bucket_name = bucket['Name']
        creation_date_utc = bucket['CreationDate'].replace(tzinfo=timezone.utc)

        if creation_date_utc > time_threshold:
            region = get_bucket_creation_region(bucket_name)
            creation_date_ist = utc_to_local(creation_date_utc, 'Asia/Kolkata')
            buckets_to_delete.append((bucket_name, region, creation_date_ist))

    return buckets_to_delete

def get_bucket_creation_region(bucket_name):
    s3_client = boto3.client('s3')
    response = s3_client.get_bucket_location(Bucket=bucket_name)
    region = response.get('LocationConstraint', 'us-east-1') or 'us-east-1'
    return region

def utc_to_local(utc_dt, tz):
    local_tz = pytz.timezone(tz)
    local_dt = utc_dt.replace(tzinfo=timezone.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)

def delete_buckets(buckets):
    if not buckets:
        print("No buckets found to delete.")
        return

    print("Buckets created within the last 24 hours:")
    s3_message_body = "S3 Buckets Deleted:\n"
    for i, (bucket_name, region, creation_date_ist) in enumerate(buckets, start=1):
        s3_message_body += f"Bucket Name: {bucket_name}\n" \
                           f"Creation Date (IST): {creation_date_ist}\n" \
                           f"Region: {region}\n\n"
        print(f"{i}. Bucket Name: {bucket_name}, Region: {region}, Creation Date (IST): {creation_date_ist}")

    bucket_names = [bucket[0] for bucket in buckets]
    deleted_buckets = []
    while True:
        user_input = input("Enter the bucket names to delete (separated by comma), or 'q' to quit: ")
        if user_input.lower() == 'q':
            break

        user_buckets = [bucket.strip() for bucket in user_input.split(',')]

        if all(bucket_name in bucket_names for bucket_name in user_buckets):
            for bucket_name in user_buckets:
                delete_bucket_confirmation(bucket_name)
                deleted_buckets.append(bucket_name)
            break
        else:
            print("Invalid bucket name(s). Please enter valid bucket name(s).")

    if deleted_buckets:
        s3_message_body += "Buckets Deleted:\n"
        for bucket_name in deleted_buckets:
            s3_message_body += f"Bucket Name: {bucket_name}\n"
    else:
        s3_message_body += "No buckets deleted."

    return s3_message_body

def delete_bucket_confirmation(bucket_name):
    while True:
        confirmation = input(f"Are you sure you want to delete bucket '{bucket_name}'? (yes/no): ")
        if confirmation.lower() == 'yes':
            delete_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' deleted successfully.")
            break
        elif confirmation.lower() == 'no':
            print(f"Skipping deletion of bucket '{bucket_name}'.")
            break
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

def delete_bucket(bucket_name):
    s3_client = boto3.client('s3')
    s3_client.delete_bucket(Bucket=bucket_name)

if __name__ == "__main__":
    buckets_created_last_24_hours = list_buckets_created_last_24_hours()
    s3_message_body = delete_buckets(buckets_created_last_24_hours)
    send_sns_notification("S3 Buckets Found", s3_message_body)
