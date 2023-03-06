from prefect import flow, task, get_run_logger

@task(name="log-example-task")
def logger_task():
    logger = get_run_logger()
    logger.info("INFO level log message from a task.")
    return logger

@flow()
def test(name):
    logger = logger_task()
    logger.info("INFO : Starting.")
    logger.info("INFO : Downloading files")
    logger.info("INFO : What is your favorite number?")
    return 42

if __name__ == "__main__":
    name = "Bob"
    test(name)