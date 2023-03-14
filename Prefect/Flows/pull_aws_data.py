from prefect_aws import S3Bucket
from prefect_sqlalchemy import DatabaseCredentials
from prefect.blocks.system import Secret
from prefect import flow, task, get_run_logger
import redshift_connector
from time import time
from datetime import datetime
import pandas as pd
import boto3
import tracemalloc
import pyarrow as pa
import pyarrow.parquet as pq

@task(name="create table")
def redshift_setup():
    database_block = DatabaseCredentials.load("redshift-credentials")
    redshift_secret = Secret.load("redshift-password")
    logger = get_run_logger()
    logger.info("INFO : Starting.")
    logger.info("INFO : Connecting to Redshift.")
    logger.info(f'INFO : Redshfit creds: host: {database_block.host}')
    logger.info(f'INFO : Redshfit creds: host: {database_block.database}')
    logger.info(f'INFO : Redshfit creds: host: {database_block.port}')
    logger.info(f'INFO : Redshfit creds: host: {database_block.username}')
    logger.info(f'INFO : Redshfit creds: host: {redshift_secret.get()}')
    conn = redshift_connector.connect(
        host=database_block.host,
        database=database_block.database,
        port=int(database_block.port),
        user=database_block.username,
        password=redshift_secret.get()
    )
    cursor = conn.cursor()
    conn.autocommit = True
    logger.info(f'INFO : ${cursor}')
    logger.info("INFO : Connected to Redshift.")
    cursor.execute('''CREATE TABLE IF NOT EXISTS AWS_SPOT_PRICES(
                   az varchar(100) NOT NULL,
                   type varchar(100) NOT NULL,
                   prod_desc varchar(100) NOT NULL,
                   spot_price DECIMAL(20,18) NOT NULL, 
                   time_stamp  timestamp NOT NULL));''')
    logger.info(f'INFO: Setup Complete')
   
@task(name="pull data and store in s3")
def pull_data_from_aws():
    logger = get_run_logger()
    logger.info("INFO : Starting.")
    
    client = boto3.client('ec2')
    
    response = client.describe_spot_price_history(
    Filters=[{},],
    AvailabilityZone='eu-central-1a',
    DryRun=False,
    EndTime=datetime(2023, 2, 21),
    InstanceTypes=[
        'a1.medium'
        ],
    MaxResults=123,
    ProductDescriptions=[
        'Linux/UNIX (Amazon VPC)'
    ],
    StartTime=datetime(2022, 2, 1)
    )
    
    data = response['SpotPriceHistory']

    df = pd.DataFrame.from_dict(data)

    table = pa.Table.from_pandas(df)

    pq.write_table(table, 'test.parquet')

    s3_bucket = S3Bucket.load("capstone-s3-bucket")
    
    s3_bucket.upload_from_path("test.parquet", "aws_data/test.parquet")
    
@task(name="copy parquet file to redshift")
def copy_to_redshift():
    logger = get_run_logger()
    logger.info("INFO : Work in progress.")
  
@flow(name="aws_to_redshift_etl") 
def pull_data_aws():
    redshift_setup()
    pull_data_from_aws()
    copy_to_redshift
 
if __name__ == "__main__":
    # starting the monitoring
    # tracemalloc.start()
    
    # function call

    pull_data_aws()
    # displaying the memory
    # print(tracemalloc.get_traced_memory())
    
    # stopping the library
    # tracemalloc.stop()
