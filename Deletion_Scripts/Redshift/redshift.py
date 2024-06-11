import boto3
from datetime import datetime, timedelta, timezone

def send_sns_notification(subject, message):
    sns_client = boto3.client('sns')
    sns_topic_arn = 'arn:aws:sns:us-east-1:654654326949:EIP'
    sns_client.publish(
        TopicArn=sns_topic_arn,
        Subject=subject,
        Message=message
    )

def check_redshift_serverless_activity():
    redshift_client = boto3.client('redshift')

    # Check if Redshift Serverless service is enabled
    try:
        redshift_client.describe_data_share()
        send_sns_notification("Redshift Serverless Enabled", "Amazon Redshift Serverless service is enabled.")
    except Exception as e:
        pass  # Redshift Serverless service is not enabled
    
    # Check if any new workgroup or namespace is created in the last 24 hours
    athena_client = boto3.client('athena')
    response_workgroups = athena_client.list_work_groups()
    workgroups = response_workgroups.get('WorkGroups', [])
    for workgroup in workgroups:
        creation_time = workgroup['CreationTime'].replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) - creation_time < timedelta(days=1):
            send_sns_notification("New Workgroup Created", f"New workgroup '{workgroup['Name']}' created in the last 24 hours.")

    redshift_data_client = boto3.client('redshift-data')
    response_clusters = redshift_client.describe_clusters()
    clusters = response_clusters.get('Clusters', [])
    for cluster in clusters:
        cluster_identifier = cluster['ClusterIdentifier']
        response_namespaces = redshift_data_client.list_schemas(ClusterIdentifier=cluster_identifier)
        namespaces = response_namespaces.get('Schemas', [])
        for namespace in namespaces:
            creation_time = namespace['CreateTime'].replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) - creation_time < timedelta(days=1):
                send_sns_notification("New Namespace Created", f"New namespace '{namespace['Name']}' created in the last 24 hours.")

if __name__ == "__main__":
    check_redshift_serverless_activity()
