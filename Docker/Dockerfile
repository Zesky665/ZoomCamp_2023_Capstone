FROM prefecthq/prefect:2.8-python3.9

RUN pip install prefect-aws

RUN pip install s3fs

WORKDIR Docker

COPY login.sh .

RUN chmod +x login.sh

RUN ./login.sh
