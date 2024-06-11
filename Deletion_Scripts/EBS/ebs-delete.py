import boto3

def send_sns_notification(subject, message):
    sns_client = boto3.client('sns')
    sns_topic_arn = 'arn:aws:sns:ap-south-1:387222771152:Techworriors'
    sns_client.publish(
        TopicArn=sns_topic_arn,
        Subject=subject,
        Message=message
    )

def check_and_delete_ebs_volumes():
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
                process_ebs_volumes(skip_regions)
                break
            else:
                print("Please re-enter the regions to skip.")
        else:
            print("No valid regions provided. Please re-enter the regions.")

def process_ebs_volumes(skip_regions):
    # Get list of all AWS regions
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

    # Flag to track if any EBS volumes are found
    ebs_volumes_found = False

    # Initialize an empty message body
    message_body = ""

    # Iterate over each region
    for region in regions:
        if region in skip_regions:
            print(f"Skipping {region} region")
            continue
        ec2_client = boto3.client('ec2', region_name=region)
        response = ec2_client.describe_volumes()
        if 'Volumes' in response and len(response['Volumes']) > 0:
            ebs_volumes = response['Volumes']
            for volume in ebs_volumes:
                ebs_volumes_found = True
                message_body += f"EBS Volume found in {region}:\n" \
                          f"Volume ID: {volume['VolumeId']}\n" \
                          f"Size: {volume['Size']} GB\n" \
                          f"Availability Zone: {volume['AvailabilityZone']}\n" \
                          f"Status: {volume['State']}\n\n"

                print(f"EBS Volume found in {region}: Volume ID - {volume['VolumeId']}, Size - {volume['Size']} GB, Status - {volume['State']}")
                # Check if the volume is attached to an instance
                if 'Attachments' in volume and volume['Attachments']:
                    for attachment in volume['Attachments']:
                        instance_id = attachment['InstanceId']
                        # Detach volume from instance
                        ec2_client.detach_volume(VolumeId=volume['VolumeId'], InstanceId=instance_id, Force=True)
                        print(f"Detached volume {volume['VolumeId']} from instance {instance_id}")
                # Delete the volume
                ec2_client.delete_volume(VolumeId=volume['VolumeId'])
                print(f"Deleted volume {volume['VolumeId']}")

    # Add description to the message body
    if ebs_volumes_found:
        message_body += "Description: EBS Volumes are Deleted"

    # Send SNS notification if EBS volumes are found
    if ebs_volumes_found:
        send_sns_notification("EBS Volume Activity Detected", message_body)
    else:
        print("EBS Volumes processed in all regions, Nothing found")

if __name__ == "__main__":
    check_and_delete_ebs_volumes()
