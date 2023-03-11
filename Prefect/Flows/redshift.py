from prefect_sqlalchemy import DatabaseCredentials
from prefect import flow, task, get_run_logger
import redshift_connector

@task(name="log-example-task")
def logger_task():
    logger = get_run_logger()
    logger.info("INFO level log message from a task.")
    return logger

@flow()
def redshift_setup():
    database_block = DatabaseCredentials.load("redshift-credentials")
    logger = logger_task()
    logger.info("INFO : Starting.")
    logger.info("INFO : Connecting to Redshift.")
    conn = redshift_connector.connect(
        host=database_block.host,
        database=database_block.database,
        port=database_block.port,
        user=database_block.username,
        password=database_block.password
    )
    cursor = conn.cursor()
    cursor.execute("create table category (catid int, cargroup varchar, catname varchar, catdesc varchar)")
    cursor.execute("copy category from 's3://testing/category_csv.txt' iam_role 'arn:aws:iam::123:role/RedshiftCopyUnload' csv;")
    cursor.execute("select * from category")
    print(cursor.fetchall())
    

if __name__ == "__main__":
    redshift_setup()