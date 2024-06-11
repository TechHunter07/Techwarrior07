import boto3

def send_sns_notification(subject, message):
    sns_client = boto3.client('sns')
    sns_topic_arn = 'arn:aws:sns:ap-south-1:387222771152:Techworriors'
    sns_client.publish(
        TopicArn=sns_topic_arn,
        Subject=subject,
        Message=message
    )

def check_and_delete_rds_clusters():
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
                process_rds_clusters(skip_regions)
                break
            else:
                print("Please re-enter the regions to skip.")
        else:
            print("No valid regions provided. Please re-enter the regions.")

def process_rds_clusters(skip_regions):
    # Get list of all AWS regions
    ec2_client = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

    # Flag to track if any RDS clusters are found
    rds_clusters_found = False

    # Initialize an empty message body
    message_body = ""

    # Iterate over each region
    for region in regions:
        if region in skip_regions:
            print(f"Skipping {region} region")
            continue
        rds_client = boto3.client('rds', region_name=region)
        response = rds_client.describe_db_clusters()
        if 'DBClusters' in response and len(response['DBClusters']) > 0:
            rds_clusters = response['DBClusters']
            for cluster in rds_clusters:
                rds_clusters_found = True
                message_body += f"RDS Cluster found in {region}:\n" \
                          f"Cluster ID: {cluster['DBClusterIdentifier']}\n" \
                          f"Status: {cluster['Status']}\n\n"

                print(f"RDS Cluster found in {region}: Cluster ID - {cluster['DBClusterIdentifier']}, Status - {cluster['Status']}")
                # Disable deletion protection
                disable_deletion_protection(rds_client, cluster['DBClusterIdentifier'])
                # Delete the RDS cluster
                delete_rds_cluster(rds_client, cluster['DBClusterIdentifier'])
                print(f"Deleted RDS Cluster {cluster['DBClusterIdentifier']}")

    # Add description to the message body
    if rds_clusters_found:
        message_body += "Description: RDS Clusters are Deleted"

    # Send SNS notification if RDS clusters are found
    if rds_clusters_found:
        send_sns_notification("RDS Cluster Activity Detected", message_body)
    else:
        print("RDS Clusters processed in all regions, Nothing found")

def disable_deletion_protection(rds_client, cluster_id):
    try:
        rds_client.modify_db_cluster(DBClusterIdentifier=cluster_id, DeletionProtection=False)
        print(f"Deletion protection disabled for RDS cluster {cluster_id}")
    except Exception as e:
        print(f"Error disabling deletion protection for RDS cluster {cluster_id}: {e}")

def delete_rds_cluster(rds_client, cluster_id):
    try:
        response = rds_client.delete_db_cluster(DBClusterIdentifier=cluster_id, SkipFinalSnapshot=True)
        print(f"RDS cluster {cluster_id} deletion initiated.")
        return response
    except Exception as e:
        print(f"Error deleting RDS cluster {cluster_id}: {e}")

if __name__ == "__main__":
    check_and_delete_rds_clusters()
