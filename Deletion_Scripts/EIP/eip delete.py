import boto3

def send_sns_notification(subject, message):
    sns_client = boto3.client('sns')
    # Replace 'your_sns_topic_arn' with the ARN of your SNS topic
    sns_topic_arn = 'arn:aws:sns:ap-south-1:387222771152:Techworriors'
    sns_client.publish(
        TopicArn=sns_topic_arn,
        Subject=subject,
        Message=message
    )

def check_and_delete_elastic_ips():
    while True:
        # Get list of all AWS regions
        ec2_client = boto3.client('ec2')
        regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

        # Prompt user for regions to skip
        skip_regions_input = input(f"Enter regions to skip from {', '.join(regions)} (comma-separated): ").split(',')
        
        # Validate regions entered by the user
        skip_regions = [region.strip() for region in skip_regions_input if region.strip() in regions]
        invalid_regions = [region.strip() for region in skip_regions_input if region.strip() not in regions]
        
        if invalid_regions:
            print(f"The following regions are invalid and will be ignored: {', '.join(invalid_regions)}")
        
        if skip_regions:
            print(f"Are you sure you want to skip these regions: {', '.join(skip_regions)}?")
            confirmation = input("Enter 'yes' to confirm, or 'no' to re-enter: ")
            if confirmation.lower() == 'yes':
                process_elastic_ips(skip_regions)
                break
            else:
                print("Please re-enter the regions to skip.")
        else:
            print("No valid regions provided. Please re-enter the regions.")

def process_elastic_ips(skip_regions):
    # Get list of all AWS regions
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

    # Flag to track if any Elastic IPs are found
    elastic_ips_found = False

    # Initialize an empty message body
    message_body = ""

    # Iterate over each region
    for region in regions:
        if region in skip_regions:
            print(f"Skipping {region} region")
            continue
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
                # Disassociate Elastic IP from instance if attached
                if 'InstanceId' in ip:
                    ec2_client.disassociate_address(
                        AssociationId=ip['AssociationId']
                    )
                    print(f"Elastic IP disassociated from instance: {ip['PublicIp']}, Allocation ID - {ip['AllocationId']}, Instance ID - {ip['InstanceId']}")
                # Release the Elastic IP
                ec2_client.release_address(AllocationId=ip['AllocationId'])
                print(f"Elastic IP released: {ip['PublicIp']}, Allocation ID - {ip['AllocationId']}")

    # Add description to the message body
    if elastic_ips_found:
        message_body += "Description: Elastic IPs are Deleted"

    # Send SNS notification if Elastic IPs are found
    if elastic_ips_found:
        send_sns_notification("Elastic IP Activity Detected", message_body)
    else:
        print("Elastic IPs processed in all regions, Nothing found")

if __name__ == "__main__":
    check_and_delete_elastic_ips()
