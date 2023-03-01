output "bucket" {
  description = "AWS S3 bucket ARN"
  value       = aws_s3_bucket.bucket.arn
}

output "dwh" {
    description = "Data Warehouse ARN"
    value       = aws_redshift_cluster.zoomcamp-capstone-dwh.arn
}

output "ecs-cluster" {
    description = "ECS Cluster ARN"
    value       = aws_ecs_cluster.capstone-cluster.arn
}

output "aws_ecs_service" {
    description = "ECS Service ARN"
    value       = aws_ecs_service.prefect_agent_service.network_configuration[0].subnets
}

