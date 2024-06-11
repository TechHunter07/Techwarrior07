import boto3

def send_sns_notification(subject, message):
    sns_client = boto3.client('sns')
    sns_topic_arn = 'arn:aws:sns:ap-south-1:387222771152:Techworriors'
    sns_client.publish(
        TopicArn=sns_topic_arn,
        Subject=subject,
        Message=message
    )

def check_and_delete_ecs_clusters():
    while True:
        # Get list of all AWS regions
        ecs_client = boto3.client('ecs')
        regions = [region['RegionName'] for region in boto3.client('ec2').describe_regions()['Regions']]

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
                delete_ecs_clusters(skip_regions)
                break
            else:
                print("Please re-enter the regions to skip.")
        else:
            print("No valid regions provided. Please re-enter the regions.")

def delete_ecs_clusters(skip_regions=[]):
    # Get list of all AWS regions
    ecs_client = boto3.client('ecs')
    regions = [region['RegionName'] for region in boto3.client('ec2').describe_regions()['Regions']]

    # Flag to track if any ECS clusters are found and deleted
    ecs_clusters_deleted = False

    # Initialize an empty message body
    message_body = ""

    # Iterate over each region
    for region in regions:
        if region in skip_regions:
            print(f"Skipping {region} region")
            continue
        ecs_client = boto3.client('ecs', region_name=region)
        response = ecs_client.list_clusters()
        if 'clusterArns' in response and len(response['clusterArns']) > 0:
            clusters = response['clusterArns']
            for cluster in clusters:
                # Stop all tasks
                tasks_response = ecs_client.list_tasks(cluster=cluster)
                if 'taskArns' in tasks_response:
                    tasks = tasks_response['taskArns']
                    # Stop tasks
                    for task in tasks:
                        ecs_client.stop_task(
                            cluster=cluster,
                            task=task
                        )
                        print(f"Task {task} stopped in cluster {cluster}")
                
                # Delete all services
                services_response = ecs_client.list_services(cluster=cluster)
                if 'serviceArns' in services_response:
                    services = services_response['serviceArns']
                    # Delete services
                    for service in services:
                        ecs_client.delete_service(
                            cluster=cluster,
                            service=service
                        )
                        print(f"Service {service} deleted in cluster {cluster}")
                
                # Deregister task definitions
                task_definitions_response = ecs_client.list_task_definitions()
                if 'taskDefinitionArns' in task_definitions_response:
                    task_definitions = task_definitions_response['taskDefinitionArns']
                    # Deregister task definitions
                    for task_definition in task_definitions:
                        ecs_client.deregister_task_definition(
                            taskDefinition=task_definition
                        )
                        print(f"Task Definition {task_definition} deregistered")

                # Delete ECS cluster
                ecs_client.delete_cluster(
                    cluster=cluster
                )
                print(f"ECS Cluster {cluster} deleted in region {region}")
                
                ecs_clusters_deleted = True
                message_body += f"ECS Cluster deleted in {region}:\n" \
                                f"Cluster ARN: {cluster}\n"
    
    # Add description to the message body
    if ecs_clusters_deleted:
        message_body += "Description: ECS Clusters Deleted"
    
    # Send SNS notification if ECS clusters are deleted
    if ecs_clusters_deleted:
        send_sns_notification("ECS Cluster Activity Detected", message_body)
    else:
        print("No ECS Clusters found")

if __name__ == "__main__":
    check_and_delete_ecs_clusters()
