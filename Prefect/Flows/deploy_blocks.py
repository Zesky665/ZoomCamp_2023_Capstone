import json
import pandas as pd
import re
from prefect import flow, task
from prefect_aws import AwsCredentials, S3Bucket, ECSTask
from prefect import get_run_logger
from pathlib import Path


def extract_value(string, value):
    found = re.search(f'{value}:(.+?),', string).group(1)
    print(found)
    return found

@task(name="deploy_aws")
def deploy_aws_credentials_block(aws_key_id, aws_key):
    
    aws_credentials = AwsCredentials(
    aws_access_key_id = aws_key_id,
    aws_secret_access_key = aws_key
    )
    
    aws_credentials.save("aws-creds", overwrite=True)
    
@task(name="deploy_s3")
def deploy_s3_block():
    logger = get_run_logger()
    logger.info("INFO: Started flow deployment.")
    
    # create a Path object with the path to the file
    path1 = Path('output.json').is_file()
    path2 = Path('Prefect/Flows/output.json').is_file()
    path3 = Path('Terraform/output.json').is_file()
    path4 = Path('../../Terraform/output.json').is_file()

    logger.info(f'INFO: {path1},{path2},{path3},{path4}')
    
    dirty_json = json.open('output.json')

    logger.info(f'INFO: {dirty_json}')
    
    data = json.load(dirty_json.read())

    # Loading the AWSCredentials
    aws_creds = AwsCredentials.load("aws-credentials")
    
    # S3 values
    s3_block_name = "deployments"
    bucket_name = data["bucket_name"]["value"]
    bucket_path = f'{bucket_name}/{s3_block_name}'
    
    logger.info(f'{s3_block_name} {bucket_name} {bucket_path}')
    
    s3 = S3Bucket(
        bucket_name=bucket_name,
        aws_credentials=aws_creds,
        basepath=bucket_path
    )
    
    s3.save("test-s3-bucket", overwrite=True)
    dirty_json.close()
    
def deploy_ecs_task_block():
    
    # Opening JSON file
    f = open('Prefect/Flows/output.js')
    
    # returns JSON object as
    # a dictionary
    data = json.loads(f)
    
    # Loading the AWSCredentials
    aws_creds = AwsCredentials.load("aws-credentials")
    
    
    # ECS Task values
    ecs_task_block_name = "flow-runner"
    ecs_task_def = data["task_definition"]["value"].replace("\"", "")
    cpu_value = ''
    cpu_memory = ''
    cpu_image = ''
    vpc_id = data["vpc_id"]["value"]
    cluster_arn = data["ecs-cluster"]["value"]
    execution_role_arn = data["execution_role"]["value"]
    task_role_arn = data["task_role"]["value"]
    launch_type = "FARGATE_SPOT"
    
    # Closing file
    f.close()
    
@flow()
def deploy_blocks(aws_key_id, aws_key):

    deploy_aws_credentials_block(aws_key_id, aws_key)
    deploy_s3_block()

if __name__ == "__main__":
    aws_key_id = ""
    aws_key = ""

    deploy_blocks(aws_key_id, aws_key)
