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

resource "aws_secretsmanager_secret" "prefect_api_key" {
  name                           = "prefect-api-key-${var.name}v3"
  recovery_window_in_days        = 0
  force_overwrite_replica_secret = true
}

resource "aws_secretsmanager_secret_version" "prefect_api_key_version" {
  secret_id     = aws_secretsmanager_secret.prefect_api_key.id
  secret_string = var.prefect_api_key
}

// Here we are configuring our Redshift cluster
resource "aws_redshift_cluster" "zoomcamp-capstone-dwh" {
  cluster_identifier = "zoomcamp-capstone-dwh"
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

resource "aws_ecs_cluster" "capstone-cluster" {
  name = "capstone-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_cluster_capacity_providers" "capstone-cluster" {
  cluster_name = aws_ecs_cluster.capstone-cluster.name

  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = "FARGATE"
  }
}

resource "aws_iam_role" "prefect_agent_execution_role" {
  name = "prefect-agent-execution-role-${var.name}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      },
    ]
  })

  inline_policy {
    name = "ssm-allow-read-prefect-api-key-${var.name}"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action = [
            "kms:Decrypt",
            "secretsmanager:GetSecretValue",
            "ssm:GetParameters"
          ]
          Effect = "Allow"
          Resource = [
            aws_secretsmanager_secret.prefect_api_key.arn
          ]
        }
      ]
    })
  }
  // AmazonECSTaskExecutionRolePolicy is an AWS managed role for creating ECS tasks and services
  managed_policy_arns = ["arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"]
}

// Create a VPC named "prefect_vpc"
resource "aws_vpc" "prefect_vpc" {
  // Here we are setting the CIDR block of the VPC
  // to the "vpc_cidr_block" variable
  cidr_block = var.vpc_cidr_block
  // We want DNS hostnames enabled for this VPC
  enable_dns_hostnames = true

  // We are tagging the VPC with the name "prefect_vpc"
  tags = {
    Name = "prefect_vpc"
  }
}

// Create an internet gateway named "prefect_igw"
// and attach it to the "prefect_vpc" VPC
resource "aws_internet_gateway" "prefect_igw" {
  // Here we are attaching the IGW to the 
  // prefect_vpc VPC
  vpc_id = aws_vpc.prefect_vpc.id

  // We are tagging the IGW with the name prefect_igw
  tags = {
    Name = "prefect_igw"
  }
}

// This data object is going to be
// holding all the available availability
// zones in our defined region
data "aws_availability_zones" "available" {
  state = "available"
}

// Create a group of public subnets based on the variable subnet_count.public
resource "aws_subnet" "prefect_public_subnet" {
  // count is the number of resources we want to create
  // here we are referencing the subnet_count.public variable which
  // current assigned to 1 so only 1 public subnet will be created
  count = var.subnet_count.public

  // Put the subnet into the "prefect_vpc" VPC
  vpc_id = aws_vpc.prefect_vpc.id

  // We are grabbing a CIDR block from the "public_subnet_cidr_blocks" variable
  // since it is a list, we need to grab the element based on count,
  // since count is 1, we will be grabbing the first cidr block 
  // which is going to be 10.0.1.0/24
  cidr_block = var.public_subnet_cidr_blocks[count.index]

  // We are grabbing the availability zone from the data object we created earlier
  // Since this is a list, we are grabbing the name of the element based on count,
  // so since count is 1, and our region is us-east-2, this should grab us-east-2a
  availability_zone = data.aws_availability_zones.available.names[count.index]

  // We are tagging the subnet with a name of "prefect_public_subnet_" and
  // suffixed with the count
  tags = {
    Name = "prefect_public_subnet_${count.index}"
  }
}

// Create a public route table named "prefect_public_rt"
resource "aws_route_table" "prefect_public_rt" {
  // Put the route table in the "prefect_vpc" VPC
  vpc_id = aws_vpc.prefect_vpc.id

  // Since this is the public route table, it will need
  // access to the internet. So we are adding a route with
  // a destination of 0.0.0.0/0 and targeting the Internet 	 
  // Gateway "prefect_igw"
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.prefect_igw.id
  }
}

// Here we are going to add the public subnets to the 
// "tutorial_public_rt" route table
resource "aws_route_table_association" "public" {
  // count is the number of subnets we want to associate with
  // this route table. We are using the subnet_count.public variable
  // which is currently 1, so we will be adding the 1 public subnet
  count = var.subnet_count.public

  // Here we are making sure that the route table is
  // "prefect_public_rt" from above
  route_table_id = aws_route_table.prefect_public_rt.id

  // This is the subnet ID. Since the "prefect_public_subnet" is a 
  // list of the public subnets, we need to use count to grab the
  // subnet element and then grab the id of that subnet
  subnet_id = aws_subnet.prefect_public_subnet[count.index].id
}

resource "aws_security_group" "prefect_agent" {
  name        = "prefect-agent-sg-${var.name}"
  description = "ECS Prefect Agent"
  vpc_id      = aws_vpc.prefect_vpc.id
}

resource "aws_security_group_rule" "https_outbound" {
  // S3 Gateway interfaces are implemented at the routing level which means we
  // can avoid the metered billing of a VPC endpoint interface by allowing
  // outbound traffic to the public IP ranges, which will be routed through
  // the Gateway interface:
  // https://docs.aws.amazon.com/AmazonS3/latest/userguide/privatelink-interface-endpoints.html
  description       = "HTTPS outbound"
  type              = "egress"
  security_group_id = aws_security_group.prefect_agent.id
  from_port         = 443
  to_port           = 443
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]

}

resource "aws_ecs_task_definition" "prefect_agent_task_definition" {
  family = "prefect-agent-${var.name}"
  cpu    = var.agent_cpu
  memory = var.agent_memory

  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"

  container_definitions = jsonencode([
    {
      name    = "prefect-agent-${var.name}"
      image   = var.agent_image
      command = ["prefect", "agent", "start", "-q", var.agent_queue_name]
      cpu     = var.agent_cpu
      memory  = var.agent_memory
      environment = [
        {
          name  = "PREFECT_API_URL"
          value = "https://api.prefect.cloud/api/accounts/${var.prefect_account_id}/workspaces/${var.prefect_workspace_id}"
        },
        {
          name  = "EXTRA_PIP_PACKAGES"
          value = var.agent_extra_pip_packages
        }
      ]
      secrets = [
        {
          name      = "PREFECT_API_KEY"
          valueFrom = aws_secretsmanager_secret.prefect_api_key.arn
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.prefect_agent_log_group.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "prefect-agent-${var.name}"
        }
      }
    }
  ])
  // Execution role allows ECS to create tasks and services
  execution_role_arn = aws_iam_role.prefect_agent_execution_role.arn
  // Task role allows tasks and services to access other AWS resources
  // Use agent_task_role_arn if provided, otherwise populate with default
  task_role_arn = var.agent_task_role_arn == null ? aws_iam_role.prefect_agent_task_role[0].arn : var.agent_task_role_arn
}

resource "aws_cloudwatch_log_group" "prefect_agent_log_group" {
  name              = "prefect-agent-log-group-${var.name}"
  retention_in_days = var.agent_log_retention_in_days
}

resource "aws_ecs_service" "prefect_agent_service" {
  name          = "prefect-agent-${var.name}"
  cluster       = aws_ecs_cluster.capstone-cluster.id
  desired_count = var.agent_desired_count
  launch_type   = "FARGATE"

  // Public IP required for pulling secrets and images
  // https://aws.amazon.com/premiumsupport/knowledge-center/ecs-unable-to-pull-secrets/
  network_configuration {
    security_groups  = [aws_security_group.prefect_agent.id]
    assign_public_ip = true
    subnets          = [for subnet in aws_subnet.prefect_public_subnet : subnet.id]
  }
  task_definition = aws_ecs_task_definition.prefect_agent_task_definition.arn
}

resource "aws_iam_role" "prefect_agent_task_role" {
  name  = "prefect-agent-task-role-${var.name}"
  count = var.agent_task_role_arn == null ? 1 : 0

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      },
    ]
  })

  inline_policy {
    name = "prefect-agent-allow-ecs-task-${var.name}"
    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [
        {
          Action = [
            "ec2:DescribeSubnets",
            "ec2:DescribeVpcs",
            "ecr:BatchCheckLayerAvailability",
            "ecr:BatchGetImage",
            "ecr:GetAuthorizationToken",
            "ecr:GetDownloadUrlForLayer",
            "ecs:DeregisterTaskDefinition",
            "ecs:DescribeTasks",
            "ecs:RegisterTaskDefinition",
            "ecs:RunTask",
            "iam:PassRole",
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:GetLogEvents",
            "logs:PutLogEvents"
          ]
          Effect   = "Allow"
          Resource = "*"
        }
      ]
    })
  }
}
