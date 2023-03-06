output "vpc_id" {
  description = "AWS VPC ID"
  value = aws_vpc.prefect_vpc.id
}

output "bucket_arn" {
  description = "AWS S3 bucket ARN"
  value       = aws_s3_bucket.bucket.arn
}

output "bucket_name" {
  description = "AWS S3 bucket Name"
  value       = aws_s3_bucket.bucket.bucket
}

output "dwh" {
    description = "Data Warehouse ARN"
    value       = aws_redshift_cluster.zoomcamp-capstone-dwh.arn
}

output "ecs-cluster" {
    description = "ECS Cluster ARN"
    value       = aws_ecs_cluster.capstone-cluster.arn
}

output "task_role" {
    description = "ECS Task Role"
    value       = aws_iam_role.prefect_agent_task_role[0].arn
}

output "execution_role" {
    description = "ECS Execution Role"
    value       = aws_iam_role.prefect_agent_execution_role.arn
}

output "aws_ecs_service" {
    description = "ECS Service ARN"
    value       = aws_ecs_service.prefect_agent_service.network_configuration[0].subnets
}


