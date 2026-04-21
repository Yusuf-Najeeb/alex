output "api_gateway_url" {
  description = "API Gateway URL (paste this into Vercel as NEXT_PUBLIC_API_URL)"
  value       = aws_apigatewayv2_api.main.api_endpoint
}

output "lambda_function_name" {
  description = "Name of the API Lambda function"
  value       = aws_lambda_function.api.function_name
}

output "setup_instructions" {
  description = "Instructions for completing the deployment"
  value = <<-EOT

    ✅ Backend (API Gateway + Lambda) deployed successfully!

    API Gateway URL: ${aws_apigatewayv2_api.main.api_endpoint}
    Lambda Function: ${aws_lambda_function.api.function_name}

    Next steps:

    1. Copy the API Gateway URL above.
    2. In your Vercel project settings, set the environment variable:
         NEXT_PUBLIC_API_URL = ${aws_apigatewayv2_api.main.api_endpoint}
       Then redeploy the Vercel project.

    3. Once you have your Vercel URL (e.g. https://alex-xyz.vercel.app):
       - Add it to terraform.tfvars in this directory:
           cors_origins = "http://localhost:3000,https://alex-xyz.vercel.app"
       - Run `terraform apply` again so the Lambda allows CORS from that origin.
       - Add the same URL to your Clerk dashboard's allowed origins.

    4. Monitor in AWS Console:
       - CloudWatch Logs: /aws/lambda/${aws_lambda_function.api.function_name}
       - API Gateway metrics

    To destroy: cd scripts && uv run destroy.py
  EOT
}
