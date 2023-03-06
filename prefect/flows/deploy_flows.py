from prefect import get_run_logger
from test_deploy import test
from prefect.deployments import Deployment
from prefect.filesystems import S3

s3_block = S3.load("deployments")

deployment = Deployment.build_from_flow(
    flow=test,
    name="test-deploy",
    parameters={"name": "Test"},
    infra_overrides={"env": {"PREFECT_LOGGING_LEVEL": "DEBUG"}},
    work_queue_name="default",
    storage=s3_block,
)

if __name__ == "__main__":
    logger = get_run_logger()
    logger.info("INFO: Started flow deployment.")
    deployment.apply()
    logger.info("INFO: Finished flow deployment.")





