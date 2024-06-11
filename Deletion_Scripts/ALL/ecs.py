import boto3
def ecs_logic():
    # Your ecs.py logic here
    print("Executing ecs.py")
def send_sns_notification(subject, message):
    sns_client = boto3.client('sns')
    # Replace 'your_sns_topic_arn' with the ARN of your SNS topic
    sns_topic_arn = 'arn:aws:sns:ap-south-1:387222771152:Techworriors'
    sns_client.publish(
        TopicArn=sns_topic_arn,
        Subject=subject,
        Message=message
    )

def check_ecs_clusters():
    # Get list of all AWS regions
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

    # Flag to track if any ECS clusters are found
    ecs_clusters_found = False

    # Initialize an empty message body
    message_body = ""

    # Iterate over each region
    for region in regions:
        if region == 'ap-south-1':
            print("Skipping ap-south-1 region")
            continue  # Skip ap-south-1 region
        ecs_client = boto3.client('ecs', region_name=region)
        response = ecs_client.list_clusters()
        if 'clusterArns' in response and len(response['clusterArns']) > 0:
            clusters = response['clusterArns']
            for cluster in clusters:
                ecs_clusters_found = True
                cluster_details = ecs_client.describe_clusters(clusters=[cluster])
                cluster_info = cluster_details['clusters'][0]
                message_body += f"ECS Cluster found in {region}:\n" \
                                f"Cluster Name: {cluster_info['clusterName']}\n" \
                                f"Cluster ARN: {cluster_info['clusterArn']}\n" \
                                f"Status: {cluster_info['status']}\n" \
                                f"Registered Container Instances: {cluster_info['registeredContainerInstancesCount']}\n" \
                                f"Running Tasks: {cluster_info['runningTasksCount']}\n\n"
                print(f"ECS Cluster found in {region}: {cluster_info['clusterName']}")

    # Add description to the message body
    if ecs_clusters_found:
        message_body += "Description: ECS Clusters Found"

    # Send SNS notification if ECS clusters are found
    if ecs_clusters_found:
        send_sns_notification("ECS Cluster Activity Detected", message_body)
    else:
        print("ECS Clusters processed in all regions, Nothing found")

if __name__ == "__main__":
    check_ecs_clusters()
