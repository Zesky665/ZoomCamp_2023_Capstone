import json
import os
import pandas as pd
import re
from prefect import flow, task
from prefect_aws import AwsCredentials, S3Bucket, ECSTask
from prefect_sqlalchemy import ConnectionComponents, SyncDriver, DatabaseCredentials
from prefect import get_run_logger
from pathlib import Path


def extract_value(string, value):
    found = re.search(f'{value}:(.+?),', string).group(1)
    print(found)
    return found

@task(name="deploy_aws")
def deploy_aws_credentials_block(aws_key_id, aws_key):
    logger = get_run_logger()
    logger.info("INFO: Started aws creds block deployment.")
    
    aws_credentials = AwsCredentials(
    aws_access_key_id = aws_key_id,
    aws_secret_access_key = aws_key
    )
    
    aws_credentials.save("aws-creds", overwrite=True)
    
    logger.info("INFO: Finished aws creds block deployment.")
    
@task(name="deploy_s3")
def deploy_s3_block():
    logger = get_run_logger()
    logger.info("INFO: Started s3 block deployment.")

    # Opening JSON file
    f = open('outputs.json')
  
    # returns JSON object as 
    # a dictionary
    data = json.load(f)

    # Loading the AWSCredentials
    aws_creds = AwsCredentials.load("aws-creds")
    
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
    
    s3.save("capstone-s3-bucket", overwrite=True)
    logger.info("INFO: Finished se bucket block deployment.")
    
task(name="deploy redshift credentials")
def deploy_redshift_credentials():
    logger = get_run_logger()
    logger.info("INFO: Started redshift block deployment.")

    # Opening JSON file
    f = open('outputs.json')
  
    # returns JSON object as 
    # a dictionary
    data = json.load(f)

    # Redshift DB values
    host = data["redshift_host"]["value"].split(":")[0]
    database = data["redshift_database"]["value"]
    port = data["redshift_port"]["value"]
    username = data["redshift_user"]["value"]
    password = data["redshift_password"]["value"]
    
    sqlalchemy_credentials = DatabaseCredentials(
        connection_info=ConnectionComponents(
            driver=SyncDriver.POSTGRESQL_PSYCOPG2,
            host=host,
            database=database,
            port=port,
            username= username,
            password= password,
        )
    )

    sqlalchemy_credentials.save("redshift-credentials", overwrite=True)
    logger.info("INFO: Finished redshift block deployment.")
    
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
    deploy_redshift_credentials()
    

if __name__ == "__main__":
    aws_key_id = ""
    aws_key = ""
    
    if ("aws_key_id" in os.environ):
        aws_key_id = os.environ['aws_key_id']
 
    if ("aws_key" in os.environ):
        aws_key = os.environ['aws_key']
    
    deploy_blocks(aws_key_id, aws_key)
