import boto3

def eip_logic():
    # Your eip.py logic here
    print("Executing eip.py")
    
def send_sns_notification(subject, message):
    sns_client = boto3.client('sns')
    # Replace 'your_sns_topic_arn' with the ARN of your SNS topic
    sns_topic_arn = 'arn:aws:sns:ap-south-1:387222771152:Techworriors'
    sns_client.publish(
        TopicArn=sns_topic_arn,
        Subject=subject,
        Message=message
    )

def check_elastic_ips():
    # Get list of all AWS regions
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

    # Flag to track if any Elastic IPs are found
    elastic_ips_found = False

    # Initialize an empty message body
    message_body = ""

    # Iterate over each region
    for region in regions:
        if region == 'ap-south-1':
            print("Skipping ap-south-1 region")
            continue  # Skip ap-south-1 region
        ec2_client = boto3.client('ec2', region_name=region)
        response = ec2_client.describe_addresses()
        if 'Addresses' in response and len(response['Addresses']) > 0:
            elastic_ips = response['Addresses']
            for ip in elastic_ips:
                elastic_ips_found = True
                message_body += f"Elastic IP found in {region}:\n" \
                          f"Public IP: {ip['PublicIp']}\n" \
                          f"Allocation ID: {ip['AllocationId']}\n" \
                          f"Instance ID: {ip.get('InstanceId', 'N/A')}\n\n"

                print(f"Elastic IP found in {region}: {ip['PublicIp']}, Allocation ID - {ip['AllocationId']}, Instance ID - {ip.get('InstanceId', 'N/A')}")

    # Add description to the message body
    if elastic_ips_found:
        message_body += "Description: Elastic IPs Found"

    # Send SNS notification if Elastic IPs are found
    if elastic_ips_found:
        send_sns_notification("Elastic IP Activity Detected", message_body)
    else:
        print("Elastic IPs processed in all regions, Nothing found")

if __name__ == "__main__":
    check_elastic_ips()
