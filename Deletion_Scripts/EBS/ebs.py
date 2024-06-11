import boto3

def send_sns_notification(subject, message):
    sns_client = boto3.client('sns')
    sns_topic_arn = 'arn:aws:sns:ap-south-1:387222771152:Techworriors'
    sns_client.publish(
        TopicArn=sns_topic_arn,
        Subject=subject,
        Message=message
    )

def check_ebs_volumes():
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
    ebs_volumes_found = False
    message_body = ""

    for region in regions:
        if region == 'ap-south-1':
            print("Skipping ap-south-1 region")
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

    if ebs_volumes_found:
        message_body += "Description: EBS Volumes Found"
    if ebs_volumes_found:
        send_sns_notification("EBS Volume Activity Detected", message_body)
    else:
        print("EBS Volumes processed in all regions, Nothing found")

if __name__ == "__main__":
    check_ebs_volumes()
