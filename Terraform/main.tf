// Here is where we are defining.
// our Terraform settings.
terraform {
  cloud {
    // The name of our organization.
    organization = "ZhareC"

    workspaces {
      // The name of our workspace.
      name = "example-workspace"
    }
  }
}

terraform {
  required_providers {
    // The only required provider we need
    // is aws, and we want version 4.15.0 .
    aws = {
      source  = "hashicorp/aws"
      version = "4.33.0"
    }
  }

  // This is the required version of Terraform.
  required_version = "~> 1.3.7"
}


// Here we are configuring our aws provider. 
// We are setting the region to the region of 
// our variable "aws_region".
provider "aws" {
  region = var.aws_region
}

// Here we are configuing our S3 bucket.
resource "aws_s3_bucket" "bucket" {
  bucket        = "my-zoomcamp-capstone-bucket-zharec"
  force_destroy = true

  tags = {
    Name        = "My bucket"
    Environment = "Dev"
  }
}

// Here we are configuring our Redshift cluster
resource "aws_redshift_cluster" "zoomcamp-capstone-dwh" {
  cluster_identifier = "tf-redshift-cluster"
  database_name      = "capstone_db"
  master_username    = "zhare_c"
  master_password    = "SuperSecretPassword1235"
  node_type          = "dc2.large"
  cluster_type       = "single-node"

  // default values
  port                             = 5439
  allow_version_upgrade            = true
  apply_immediately                = true
  number_of_nodes                  = 1
  publicly_accessible              = true
  skip_final_snapshot              = true // default is false, prevents destroy action
  maintenance_track_name           = "current"
  manual_snapshot_retention_period = -1


  tags = {
    Name        = "Redshift Serverless Capstone"
    Environment = "Dev"
  }
}