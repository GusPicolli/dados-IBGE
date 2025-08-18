locals {
  repository_name = "etl_coningecko"
}

resource "aws_ecr_repository" "repository_pipeline" {
  name = local.repository_name

  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = false
  }
}

resource "null_resource" "docker_ecr" {
  triggers = {
    ecr_repository_name = local.repository_name
  }

  provisioner "local-exec" {
    command = <<EOF
      docker build -t ${local.repository_name}:latest -f ../docker/Dockerfile_app ../ 
    EOF
  }

  provisioner "local-exec" {
    command = <<EOF
      docker tag ${local.repository_name}:latest ${aws_ecr_repository.repository_pipeline.repository_url}:latest
    EOF
  }

  provisioner "local-exec" {
    command = <<EOF
      docker push ${aws_ecr_repository.repository_pipeline.repository_url}:latest
    EOF
  }

  depends_on = [aws_ecr_repository.repository_pipeline]
}

output "repository_url" {
  description = "The URL of the ECR repository."
  value       = aws_ecr_repository.repository_pipeline.repository_url
}

output "repository_name" {
  description = "The name of the ECR repository."
  value       = aws_ecr_repository.repository_pipeline.name
}