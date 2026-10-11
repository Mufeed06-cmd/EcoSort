#!/usr/bin/env bash
# ==============================================================================
# AI Waste Segregation Advisor — AWS Deployment Script
# ==============================================================================
set -euo pipefail

STACK_NAME="ai-waste-segregation-advisor"
DEFAULT_REGION="${AWS_REGION:-us-east-1}"
BEDROCK_MODEL_ID="${BEDROCK_MODEL_ID:-anthropic.claude-3-haiku-20240307-v1:0}"

echo "======================================================================"
echo "  🌿 AI Waste Segregation Advisor — AWS Deployment Helper"
echo "======================================================================"
echo "Stack:            ${STACK_NAME}"
echo "Region:           ${DEFAULT_REGION}"
echo "Bedrock Model:    ${BEDROCK_MODEL_ID}"
echo "======================================================================"

# Check AWS CLI
if ! command -v aws &> /dev/null; then
  echo "❌ AWS CLI is not installed or not in PATH."
  echo "Please install the AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
  exit 1
fi

# Verify AWS Credentials
echo "🔍 Checking AWS credentials..."
if ! aws sts get-caller-identity > /dev/null 2>&1; then
  echo "❌ AWS credentials are not configured or invalid."
  echo "Run 'aws configure' to set up AWS Access Key, Secret Key, and Region."
  exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
echo "✅ Authenticated as AWS Account: ${ACCOUNT_ID} in ${DEFAULT_REGION}"

# Check for SAM CLI
if command -v sam &> /dev/null; then
  echo "🚀 Detected AWS SAM CLI. Building and deploying via SAM..."
  cd "$(dirname "$0")"
  sam build -t template.yaml
  sam deploy \
    --stack-name "${STACK_NAME}" \
    --region "${DEFAULT_REGION}" \
    --capabilities CAPABILITY_IAM \
    --resolve-s3 \
    --parameter-overrides \
      "BedrockModelId=${BEDROCK_MODEL_ID}" \
      "EnableMockMode=false" \
    --no-confirm-changeset
  echo "======================================================================"
  echo "✅ AWS SAM Deployment Complete!"
  API_URL=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --region "${DEFAULT_REGION}" \
    --query "Stacks[0].Outputs[?OutputKey=='ApiEndpoint'].OutputValue" \
    --output text)
  echo "📡 Your live API Endpoint is: ${API_URL}"
  echo "👉 Update your frontend .env file: VITE_API_URL=${API_URL}"
  echo "======================================================================"
else
  echo "ℹ️ AWS SAM CLI not detected. Deploying via standard AWS CLI..."

  DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  BUILD_DIR="/tmp/waste-advisor-build"
  rm -rf "${BUILD_DIR}"
  mkdir -p "${BUILD_DIR}/package"

  echo "📦 Packaging Lambda function code..."
  cp -r "${DIR}/backend" "${BUILD_DIR}/package/"
  # Remove tests and pycache from package
  rm -rf "${BUILD_DIR}/package/backend/tests" "${BUILD_DIR}/package/backend/__pycache__"

  cd "${BUILD_DIR}/package"
  zip -r "${BUILD_DIR}/function.zip" . > /dev/null

  FUNCTION_NAME="ai-waste-segregation-advisor-lambda"
  ROLE_NAME="ai-waste-advisor-lambda-role"

  echo "🔐 Ensuring IAM Execution Role (${ROLE_NAME})..."
  TRUST_POLICY='{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}'

  ROLE_ARN=$(aws iam get-role --role-name "${ROLE_NAME}" --query "Role.Arn" --output text 2>/dev/null || true)
  if [ -z "${ROLE_ARN}" ]; then
    echo "Creating IAM Role..."
    ROLE_ARN=$(aws iam create-role --role-name "${ROLE_NAME}" --assume-role-policy-document "${TRUST_POLICY}" --query "Role.Arn" --output text)
    aws iam put-role-policy --role-name "${ROLE_NAME}" --policy-name "BedrockAndLogsAccess" --policy-document file://"${DIR}/deployment/iam-policy.json"
    echo "Waiting 10s for IAM role replication..."
    sleep 10
  fi

  echo "⚡ Creating or updating Lambda function (${FUNCTION_NAME})..."
  if aws lambda get-function --function-name "${FUNCTION_NAME}" --region "${DEFAULT_REGION}" > /dev/null 2>&1; then
    aws lambda update-function-code \
      --function-name "${FUNCTION_NAME}" \
      --zip-file "fileb://${BUILD_DIR}/function.zip" \
      --region "${DEFAULT_REGION}" > /dev/null
    aws lambda update-function-configuration \
      --function-name "${FUNCTION_NAME}" \
      --environment "Variables={AWS_REGION=${DEFAULT_REGION},BEDROCK_MODEL_ID=${BEDROCK_MODEL_ID},MOCK_MODE=false}" \
      --region "${DEFAULT_REGION}" > /dev/null
  else
    aws lambda create-function \
      --function-name "${FUNCTION_NAME}" \
      --runtime "python3.12" \
      --role "${ROLE_ARN}" \
      --handler "backend.lambda_handler.lambda_handler" \
      --zip-file "fileb://${BUILD_DIR}/function.zip" \
      --timeout 30 \
      --memory-size 512 \
      --environment "Variables={AWS_REGION=${DEFAULT_REGION},BEDROCK_MODEL_ID=${BEDROCK_MODEL_ID},MOCK_MODE=false}" \
      --region "${DEFAULT_REGION}" > /dev/null
  fi

  echo "✅ Lambda function deployed!"
  echo "Use AWS API Gateway console or SAM template to expose POST /analyze."
fi
