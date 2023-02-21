# Cloud Pricing DE Capstone Project

This project automaticaly ingests, stores, transforms the latest price data from the three major cloud providers (AWS, GCP, Azure) for tracking and analysis. 

This GithHub repository fulfills the final capstone project for the Data Engineering Zoomcamp by DataTalks.Club.

** Insert the diagram here **

# Dashboard

** Insert link to Dashboard **

** Insert pricture of Dashboard**


# Technical Challenge

Data Engineers need to keep costs in mind as they build out data infrastructure. To accomplish this they need easily accessible and queryable data. This can be accomplished by pulling data from all of the relevant sources and wrangling into an uniform format and making it acessible via a self-service tool. 

To be useful this implementation needs to be:
 - Fully Automated
 - Reliable
 - Scalable
 - Cost Effective

 # Technology Utilised

 - Infractructure as code (IaC): Terraform
 - Workflow orchestration: Prefect
 - Containerisation: Docker
 - Data Lake: AWS S3
 - Data Warehouse: AWS Redshift
 - Transformations: dbt
 - Visualization: To be decided. 

 # Dataset

 The data comes from the public REST API from the AWS, GCP and Azure services respectively. 

 AWS: 
    - URL
    - Parameters
    - Format

 GCP: 
    - URL
    - Parameters
    - Format

 Azure: 
    - URL
    - Parameters
    - Format


# Infrastructure as code 

## Terrafrom
The terrafrom script used to deploy all of the necessary services. 

## Docker
The dockerfile optimised for the specific task. 

## Github Actions
The GitHub Actions scripts enabling the full deployment. 


# Data Transformation

- JSON data is recieved from the response. 

- The data is parsed and moved to a pandas dataframe. 

- The dataframe is converted to a parquet file with a timestamp and cloud code.

- The parquet file is uploaded to a S3 bucket. Parquet allows for much smalled files, thus saving on storage costs. 

# Data Modeling

Needs to be looked into

# Data Storage

- The raw data is stored as .parqet files in the S3 bucket. 
- Staging data is stored in the DWH. 
- Production data AKA the datamarts are stored on the DWH. 

# Prefect Orchestration

The Flow does the follwing on a daily schedule: 

    1. Parametrizes the API endpoints and clud secrets using Prefect blocks. 
    2. Uses the python requests built-in library to get API responses. 
    3. Formats the data and saves it to the S3 bucket.
    4. Loads the parquet file to the DWH. 
    5. Triggers the dbt_run command. 

# Prefect Flow diagram

** Insert Prefect Flow Diagram **

# dbt Transformation

Take data from staging data and move it into several datamart tables. 

## dbt Lineage Graph

** Insert picture of dbt graph **


# Visualisation

Insert instructions on how to plug visualisation tool into database. 


# Additional Tasks

- Implement testing.
- Set up daily report pushed via slack or gmail. 

# Acknowledgements

Thanks to the instructors: 

-
-
-
-

My teammates and mentors: 

-
-
-

# Contact information

LinkedIn
Website