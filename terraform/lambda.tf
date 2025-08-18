locals {
  lambda_parameters = {
    ingestao = {
      name              = "coingecko_etl_ingestao"
      variables = {
        RAW_CONFIG = "./config.ingestion.json"
        RAW_PATH   = "s3://dataops-treinamento/coingecko_etl/raw"
      }
      timeout           = "60"
      memory_size       = "512"
      ephemeral_storage = "512"
      command           = "app.ingestion_handler"
      vpc_config        = false
    },
    preparacao = {
      name              = "coingecko_etl_preparacao"
      variables = {
        WORK_CONFIG = "./config.preparation.json"
        WORK_PATH   = "s3://dataops-treinamento/coingecko_etl/work"
        RAW_PATH   = "s3://dataops-treinamento/coingecko_etl/raw"
      }
      timeout           = "60"
      memory_size       = "512"
      ephemeral_storage = "512"
      command           = "app.preparation_handler"
      vpc_config        = false
    }
  }
}

resource "aws_lambda_function" "lambda" {
  for_each      = local.lambda_parameters
  function_name = each.value.name

  tags = {
    Name = each.value.name
  }
  role = aws_iam_role.lambda_role.arn

  image_config {
    command = [each.value.command]
  }

  environment {
    variables = each.value.variables
  }

  package_type = "Image"
  image_uri    = "${aws_ecr_repository.repository_pipeline.repository_url}:latest"

  timeout = each.value.timeout

  memory_size = each.value.memory_size

  ephemeral_storage {
    size = each.value.ephemeral_storage
  }

  depends_on = [null_resource.docker_ecr]
}

resource "aws_iam_role" "lambda_role" {
  name = "lambda_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action    = "sts:AssumeRole",
      Effect    = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_ecr_policy" {
  name = "lambda_ecr_policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability"
        ],
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_s3_policy" {
  name = "lambda_s3_policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:ListBucket"
        ],
        Resource = [
          "arn:aws:s3:::dataops-treinamento",
          "arn:aws:s3:::dataops-treinamento/*"
        ]
      }
    ]
  })
}