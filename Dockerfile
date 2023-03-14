FROM prefecthq/prefect:2.8-python3.9

RUN pip install prefect-aws

RUN pip install s3fs

RUN pip install SQLAlchemy

RUN pip install psycopg2-binary

RUN pip install prefect-sqlalchemy

RUN pip install redshift_connector

RUN pip install pandas

RUN pip install boto3

RUN pip install pyarrow

COPY Prefect/Flows opt/Prefect/Flows

COPY login.sh .

RUN chmod +x login.sh

RUN ./login.sh
