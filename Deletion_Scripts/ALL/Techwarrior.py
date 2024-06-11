import subprocess
import logging
import boto3
import time

# Configure logging
logging.basicConfig(filename='script_errors.log', level=logging.ERROR)

# List of Python scripts to execute
scripts = ['policychecker.py', 'ebs.py', 'EC2.py', 'ecs.py', 'eip.py', 'natgateway.py', 'rds.py', 'S3.py']

# Function to send SNS notification
def send_sns_notification(subject, message):
    sns_client = boto3.client('sns', region_name='ap-south-1')
    sns_topic_arn = 'arn:aws:sns:ap-south-1:387222771152:Techworriors'
    sns_client.publish(
        TopicArn=sns_topic_arn,
        Subject=subject,
        Message=message
    )

# Function to execute a Python script and capture its output
def run_script(script_name):
    start_time = time.time()  # Record start time for each script
    print(f"Running {script_name} script...")
    try:
        output = subprocess.check_output(['python3', script_name], stderr=subprocess.STDOUT, universal_newlines=True)
        with open('script_output.log', 'a') as log_file:
            log_file.write(f"Running {script_name} script...\n")
            log_file.write(output)
            log_file.write('\n')
    except subprocess.CalledProcessError as e:
        error_message = f"Error executing {script_name} script: {e.output}"
        error_timestamp = time.strftime('%Y-%m-%d %H:%M:%S')  # Record timestamp when error occurred
        logging.error(f"{error_timestamp}: {error_message}")  # Include timestamp in the error log
        send_sns_notification(f"Error executing {script_name} script", error_message)
    finally:
        end_time = time.time()  # Record end time for each script
        execution_time = end_time - start_time
        with open('script_output.log', 'a') as log_file:
            log_file.write(f"Execution completed time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_file.write(f"Script execution time: {execution_time:.2f} seconds\n")

# Record overall start time
overall_start_time = time.time()

# Execute each script in the list
for script in scripts:
    run_script(script)

# Calculate overall execution time
overall_end_time = time.time()
overall_execution_time = overall_end_time - overall_start_time

# Append total execution time to the log file
with open('script_output.log', 'a') as log_file:
    log_file.write(f"All scripts executed. Total time taken: {overall_execution_time:.2f} seconds\n")
