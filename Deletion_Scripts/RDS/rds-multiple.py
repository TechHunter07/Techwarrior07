import boto3

def send_sns_notification(subject, message):
    sns_client = boto3.client('sns')
    sns_topic_arn = 'arn:aws:sns:us-east-1:654654326949:EIP'
    sns_client.publish(
        TopicArn=sns_topic_arn,
        Subject=subject,
        Message=message
    )

def check_rds_instances():
    ec2_client = boto3.client('ec2')
    regions_to_skip = ['ap-south-1', 'us-east-1']  # Define regions to skip
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]
    rds_instances_found = False
    rds_message_body = ""

    for region in regions:
        if region in regions_to_skip:
            print(f"Skipping {region} region")
            continue
            
        rds_client = boto3.client('rds', region_name=region)
        response = rds_client.describe_db_instances()
        if 'DBInstances' in response and len(response['DBInstances']) > 0:
            rds_instances = response['DBInstances']
            for instance in rds_instances:
                rds_instances_found = True
                rds_message_body += f"RDS Instance found in {region}:\n" \
                          f"Instance ID: {instance['DBInstanceIdentifier']}\n" \
                          f"Engine: {instance['Engine']}\n" \
                          f"Status: {instance['DBInstanceStatus']}\n\n"

                print(f"RDS Instance found in {region}: Instance ID - {instance['DBInstanceIdentifier']}, Engine - {instance['Engine']}, Status - {instance['DBInstanceStatus']}")

    if rds_instances_found:
        rds_message_body += "Description: RDS Instances Found"
        send_sns_notification("RDS Instance Activity Detected", rds_message_body)
    else:
        print("RDS Instances processed in all regions, Nothing found")

if __name__ == "__main__":
    check_rds_instances()
