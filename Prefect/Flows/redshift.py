from prefect_sqlalchemy import DatabaseCredentials
from prefect.blocks.system import Secret
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
    redshift_secret = Secret.load("redshift-password")
    logger = logger_task()
    logger.info("INFO : Starting.")
    logger.info("INFO : Connecting to Redshift.")
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
    cursor.execute('''CREATE TABLE Persons (
        PersonID int,
        LastName varchar(255),
        FirstName varchar(255),
        Address varchar(255),
        City varchar(255)
    );''')
    result = cursor.execute("INSERT INTO Persons ( PersonID, LastName, FirstName, Address, City) VALUES (1, 'Testerson', 'Tester', 'Test-St', 'Testvile')")
    logger.info(f'INFO: {result}')

    

if __name__ == "__main__":
    redshift_setup()