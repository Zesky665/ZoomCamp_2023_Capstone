output "bucket" {
  description = "AWS S3 bucket ARN"
  value       = aws_s3_bucket.bucket.arn
}

output "dwh" {
    description = "Data Warehouse ARN"
    value       = aws_redshift_cluster.zoomcamp-capstone-dwh.arn
}
