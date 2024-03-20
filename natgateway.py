import boto3

def natgateway_logic():
    # Your natgateway.py logic here
    print("Executing natgateway.py")

def send_sns_notification(subject, message):
    sns_client = boto3.client('sns')
    # Replace 'your_sns_topic_arn' with the ARN of your SNS topic
    sns_topic_arn = 'arn:aws:sns:ap-south-1:387222771152:Techworriors'
    sns_client.publish(
        TopicArn=sns_topic_arn,
        Subject=subject,
        Message=message
    )

def check_nat_gateways():
    # Get list of all AWS regions
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

    # Flag to track if any NAT Gateways are found
    nat_gateways_found = False

    # Initialize an empty message body
    message_body = ""

    # Iterate over each region
    for region in regions:
        if region == 'ap-south-1':
            print("Skipping ap-south-1 region")
            continue  # Skip ap-south-1 region
        ec2_client = boto3.client('ec2', region_name=region)
        response = ec2_client.describe_nat_gateways()
        if 'NatGateways' in response and len(response['NatGateways']) > 0:
            nat_gateways = response['NatGateways']
            for nat_gateway in nat_gateways:
                nat_gateways_found = True
                message_body += f"NAT Gateway found in {region}:\n" \
                                f"NAT Gateway ID: {nat_gateway['NatGatewayId']}\n" \
                                f"Public IP: {nat_gateway['NatGatewayAddresses'][0]['PublicIp']}\n" \
                                f"Subnet ID: {nat_gateway['SubnetId']}\n\n"

                print(f"NAT Gateway found in {region}: {nat_gateway['NatGatewayId']}, "
                      f"Public IP - {nat_gateway['NatGatewayAddresses'][0]['PublicIp']}, "
                      f"Subnet ID - {nat_gateway['SubnetId']}")

    # Add description to the message body
    if nat_gateways_found:
        message_body += "Description: NAT Gateways Found"

    # Send SNS notification if NAT Gateways are found
    if nat_gateways_found:
        send_sns_notification("NAT Gateway Activity Detected", message_body)
    else:
        print("NAT Gateways processed in all regions, Nothing found")

if __name__ == "__main__":
    check_nat_gateways()
