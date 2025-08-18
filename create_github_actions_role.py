import json
import boto3

# Configurações
aws_region = "us-east-1"
account_id = ""
github_username = "GusPicolli"
repository_name = "dados-CoinGecko"
s3_bucket_name = ""

# Cliente boto3
iam_client = boto3.client('iam', region_name=aws_region)

# Nome da role
role_name = "github_actions_role_coingecko"

# Política de confiança
assume_role_policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Federated": f"arn:aws:iam::{account_id}:oidc-provider/token.actions.githubusercontent.com"
            },
            "Action": "sts:AssumeRoleWithWebIdentity",
            "Condition": {
                "StringEquals": {
                    "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
                    "token.actions.githubusercontent.com:sub": f"repo:{github_username}/{repository_name}:*"
                }
            }
        }
    ]
}

# Criar a role
response = iam_client.create_role(
    RoleName=role_name,
    AssumeRolePolicyDocument=json.dumps(assume_role_policy_document),
    Description="Role for GitHub Actions to access AWS resources",
)
role_arn = response['Role']['Arn']
print(f"Created role with ARN: {role_arn}")

# Anexar política gerenciada AWSLambdaBasicExecutionRole
iam_client.attach_role_policy(
    RoleName=role_name,
    PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
)

# Política ECR
ecr_policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:BatchCheckLayerAvailability"
            ],
            "Resource": "*"
        }
    ]
}
iam_client.put_role_policy(
    RoleName=role_name,
    PolicyName="github_actions_ecr_policy_coingecko",
    PolicyDocument=json.dumps(ecr_policy_document)
)

# Política S3
s3_policy_document = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:ListBucket"
            ],
            "Resource": [
                f"arn:aws:s3:::{s3_bucket_name}",
                f"arn:aws:s3:::{s3_bucket_name}/*"
            ]
        }
    ]
}
iam_client.put_role_policy(
    RoleName=role_name,
    PolicyName="github_actions_s3_policy_coingecko",
    PolicyDocument=json.dumps(s3_policy_document)
)

print(f"Attached policies to role {role_name}")