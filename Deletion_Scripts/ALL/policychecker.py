import boto3

# Initialize IAM and SNS clients
iam_client = boto3.client('iam')
sns_client = boto3.client('sns')

# IAM user name
user_name = 'TechWorrior'

# Expected read-only policies (including inline policies)
expected_policies = ['AmazonEC2ReadOnlyAccess', 'AmazonRDSReadOnlyAccess', 'AmazonS3ReadOnlyAccess']

# Retrieve managed policies attached to the IAM user
response_managed = iam_client.list_attached_user_policies(UserName=user_name)
attached_managed_policies = [policy['PolicyName'] for policy in response_managed['AttachedPolicies']]

# Retrieve inline policies attached to the IAM user
response_inline = iam_client.list_user_policies(UserName=user_name)
attached_inline_policies = response_inline['PolicyNames']

# Combine managed and inline policies
attached_policies = attached_managed_policies + attached_inline_policies

# Check for unexpected policies
unexpected_policies = [policy for policy in attached_policies if policy not in expected_policies]

# Remove ElasticBlockStoreReadOnly policy from unexpected policies
unexpected_policies = [policy for policy in unexpected_policies if policy != 'ElasticBlockStoreReadOnly']

# If unexpected policies are found (excluding ElasticBlockStoreReadOnly), send a notification
if unexpected_policies:
    message = f"Unexpected policies attached to IAM user {user_name}:"
    for policy in unexpected_policies:
        message += f"\n{policy}"
    sns_client.publish(TopicArn='arn:aws:sns:ap-south-1:387222771152:Techworriors', Message=message, Subject='Unexpected IAM Policies')
    print("Notification sent: Unexpected policies found.")
else:
    print("No unexpected policies found.")
