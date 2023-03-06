import json
import re
from prefect_aws import AwsCredentials, S3Bucket, ECSTask

def extract_value(string, value):
    found = re.search(f'{value}:(.+?),', string).group(1)
    print(found)
    return found

def deploy_aws_credentials_block(aws_key_id, aws_key):
    
    aws_credentials = AwsCredentials(
    aws_access_key_id = aws_key_id,
    aws_secret_access_key = aws_key
    )
    
    aws_credentials.save("aws-creds", overwrite=True)
    
def deploy_s3_block():
    # Opening JSON file
    f = open('output.json',)
    
    # returns JSON object as
    # a dictionary
    data = json.load(f)
    
    # Loading the AWSCredentials
    aws_creds = AwsCredentials.load("aws-credentials")
    
    # S3 values
    s3_block_name = "deployments"
    bucket_name = data["bucket_name"]["value"]
    bucket_path = f'{bucket_name}/{s3_block_name}'
    
    s3 = S3Bucket(
        bucket_name=bucket_name,
        aws_credentials=aws_creds,
        basepath=bucket_path
    )
    
    s3.save("test-s3-bucket", overwrite=True)
    
    f.close()
    
def deploy_ecs_task_block():
    
    # Opening JSON file
    f = open('output.json',)
    
    # returns JSON object as
    # a dictionary
    data = json.load(f)
    
    # Loading the AWSCredentials
    aws_creds = AwsCredentials.load("aws-credentials")
    
    
    # ECS Task values
    ecs_task_block_name = "flow-runner"
    ecs_task_def = data["task_definition"]["value"].replace("\"", "")
    cpu_value = extract_value(ecs_task_def, "cpu")
    cpu_memory = extract_value(ecs_task_def, "memory")
    cpu_image = extract_value(ecs_task_def, "image")
    vpc_id = data["vpc_id"]["value"]
    cluster_arn = data["ecs-cluster"]["value"]
    execution_role_arn = data["execution_role"]["value"]
    task_role_arn = data["task_role"]["value"]
    launch_type = "FARGATE_SPOT"
    
    # Closing file
    f.close()


if __name__ == "__main__":
    aws_key_id = "erewrewrwerwe"
    aws_key = "232312312312"
    deploy_aws_credentials_block(aws_key_id, aws_key)
    deploy_s3_block()





