from prefect import get_run_logger, flow, task
from test_deploy import test
from redshift import redshift_setup
from prefect.deployments import Deployment
from prefect_aws import S3Bucket, ECSTask

@task()
def deploy_test_flow():
    logger = get_run_logger()
    logger.info("INFO: Started test flow deployment.")
    s3_block = S3Bucket.load("capstone-s3-bucket")

    deployment = Deployment.build_from_flow(
        flow=test,
        name="test-deploy",
        parameters={"name": "Test"},
        infra_overrides={"env": {"PREFECT_LOGGING_LEVEL": "DEBUG"}},
        work_queue_name="default",
        storage=s3_block,
    )
    
    deployment.apply()
    logger.info("INFO: Finished test flow deployment.")

@task()
def deploy_deploy_flow():
    logger = get_run_logger()
    logger.info("INFO: Started deploy flow deployment.")
    s3_block = S3Bucket.load("capstone-s3-bucket")

    deployment = Deployment.build_from_flow(
        flow=deploy_flows,
        name="deploy-deploy",
        parameters={"name": "Deploy Flows"},
        infra_overrides={"env": {"PREFECT_LOGGING_LEVEL": "DEBUG"}},
        work_queue_name="default",
        storage=s3_block,
    )
    
    deployment.apply()
    logger.info("INFO: Finished deploy flow deployment.")
    
@task()
def deploy_redshift_flow():
    logger = get_run_logger()
    logger.info("INFO: Started redshift flow deployment.")
    s3_block = S3Bucket.load("capstone-s3-bucket")

    deployment = Deployment.build_from_flow(
        flow=redshift_setup,
        name="deploy-redshift",
        parameters={"name": "Deploy Redshift"},
        infra_overrides={"env": {"PREFECT_LOGGING_LEVEL": "DEBUG"}},
        work_queue_name="default",
        storage=s3_block,
    )
    
    deployment.apply()
    logger.info("INFO: Finished redshift flow deployment.")
    
@flow()
def deploy_flows():
    logger = get_run_logger()
    logger.info("INFO: Started flow deployment.")
    deploy_test_flow()
    deploy_deploy_flow()
    deploy_redshift_flow()
    logger.info("INFO: Finished flow deployment.")

if __name__ == "__main__":
    deploy_flows()
