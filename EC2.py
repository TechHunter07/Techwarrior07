import boto3
def EC2_logic():
    # Your EC2.py logic here
    print("Executing EC2.py")
def send_sns_notification(subject, message):
    sns_client = boto3.client('sns')
    # Replace 'your_sns_topic_arn' with the ARN of your SNS topic
    sns_topic_arn = 'arn:aws:sns:ap-south-1:387222771152:Techworriors'
    sns_client.publish(
        TopicArn=sns_topic_arn,
        Subject=subject,
        Message=message
    )

def check_ec2_instances():
    # Get list of all AWS regions
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

    # Flag to track if any EC2 instances are found
    instances_found = False

    # Initialize an empty message body
    message_body = ""

    # Iterate over each region
    for region in regions:
        if region == 'ap-south-1':
            print("Skipping ap-south-1 region")
            continue  # Skip ap-south-1 region
        ec2_resource = boto3.resource('ec2', region_name=region)
        instances = list(ec2_resource.instances.all())
        if instances:
            instances_found = True
            for instance in instances:
                message_body += f"  EC2 instance found in {region}:\n"
                message_body += f"  Instance ID: {instance.id}\n"
                message_body += f"  Instance Type: {instance.instance_type}\n"
                message_body += f"  VPC ID: {instance.vpc_id}\n\n"
                print(f"EC2 instance found in {region}: Instance ID: {instance.id}, Instance Type: {instance.instance_type}, VPC ID: {instance.vpc_id}")

    # Send SNS notification if EC2 instances are found
    if instances_found:
        send_sns_notification("EC2 Instance Activity Detected", message_body)
    else:
        print("No EC2 instances found in any region")

if __name__ == "__main__":
    check_ec2_instances()
