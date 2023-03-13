output "vpc_id" {
  description = "AWS VPC ID"
  value       = aws_vpc.prefect_vpc.id
}

output "bucket_arn" {
  description = "AWS S3 bucket ARN"
  value       = aws_s3_bucket.bucket.arn
}

output "bucket_name" {
  description = "AWS S3 bucket Name"
  value       = aws_s3_bucket.bucket.bucket
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

output "redshift_host" {
  description = "Redshift host adress"
  value       = aws_redshiftserverless_workgroup.zoomcamp-capstone-dwh-workgroup.endpoint
}

output "redshift_port" {
  description = "Redshift port"
  value       = aws_redshiftserverless_workgroup.zoomcamp-capstone-dwh-workgroup.port
}

output "redshift_database" {
  description = "Redshift database"
  value       = aws_redshiftserverless_namespace.zoomcamp-capstone-dwh-namespace.db_name 
}

output "redshift_user" {
  description = "Redshift admin user"
  value       = aws_redshiftserverless_namespace.zoomcamp-capstone-dwh-namespace.admin_username
  sensitive = true
}
output "redshift_password" {
  description = "Redshift dataabse password"
  value       = aws_redshiftserverless_namespace.zoomcamp-capstone-dwh-namespace.admin_user_password
  sensitive   = true
}

