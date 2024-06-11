import boto3

def send_sns_notification(subject, message):
    sns_client = boto3.client('sns')
    sns_topic_arn = 'arn:aws:sns:ap-south-1:387222771152:Techworriors'
    sns_client.publish(
        TopicArn=sns_topic_arn,
        Subject=subject,
        Message=message
    )

def check_and_delete_nat_gateways():
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
                process_nat_gateways(skip_regions)
                break
            else:
                print("Please re-enter the regions to skip.")
        else:
            print("No valid regions provided. Please re-enter the regions.")

def process_nat_gateways(skip_regions):
    # Get list of all AWS regions
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

    # Flag to track if any NAT Gateways are found and deleted
    nat_gateways_deleted = False

    # Initialize an empty message body
    message_body = ""

    # Iterate over each region
    for region in regions:
        if region in skip_regions:
            print(f"Skipping {region} region")
            continue
        ec2_client = boto3.client('ec2', region_name=region)
        response = ec2_client.describe_nat_gateways()
        if 'NatGateways' in response and len(response['NatGateways']) > 0:
            nat_gateways = response['NatGateways']
            for nat_gateway in nat_gateways:
                nat_gateway_id = nat_gateway['NatGatewayId']
                # Check if NAT Gateway is associated with any Elastic IPs
                if nat_gateway['NatGatewayAddresses']:
                    elastic_ip_info = nat_gateway['NatGatewayAddresses'][0]
                    if 'PublicIp' in elastic_ip_info:
                        elastic_ip = elastic_ip_info['PublicIp']
                        subnet_id = nat_gateway['SubnetId']
                        
                        # Disassociate Elastic IP from NAT Gateway
                        ec2_client.disassociate_address(
                            PublicIp=elastic_ip
                        )
                        print(f"Elastic IP disassociated from NAT Gateway {nat_gateway_id}: {elastic_ip}")

                        # Release the Elastic IP
                        ec2_client.release_address(
                            AllocationId=elastic_ip_info['AllocationId']
                        )
                        print(f"Elastic IP released: {elastic_ip}")
                    
                # Delete NAT Gateway
                ec2_client.delete_nat_gateway(
                    NatGatewayId=nat_gateway_id
                )
                print(f"NAT Gateway {nat_gateway_id} deleted")
                
                nat_gateways_deleted = True
                message_body += f"NAT Gateway deleted in {region}:\n" \
                                f"NAT Gateway ID: {nat_gateway_id}\n"
    
    # Add description to the message body
    if nat_gateways_deleted:
        message_body += "Description: NAT Gateways Deleted"
    
    # Send SNS notification if NAT Gateways are deleted
    if nat_gateways_deleted:
        send_sns_notification("NAT Gateway Activity Detected", message_body)
    else:
        print("No NAT Gateways found associated with Elastic IPs")

if __name__ == "__main__":
    check_and_delete_nat_gateways()
