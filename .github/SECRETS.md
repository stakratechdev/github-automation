# Secrets Management Guide

## GitHub Secrets Configuration

For GitHub Actions CI/CD, configure the following secrets in your repository:

### Required Secrets

1. **GITHUB_TOKEN**
   - Description: GitHub Personal Access Token with repo scope
   - Create: GitHub Settings → Developer settings → Personal access tokens → Generate new token
   - Required scopes: `repo`, `workflow`

2. **LLM_API_KEY**
   - Description: API key for your LLM provider (OpenAI, Anthropic)
   - Create: OpenAI Platform → API keys or Anthropic Console

### Optional Secrets

3. **DOCKER_REGISTRY_TOKEN**
   - Description: Docker registry authentication token
   - Required for pushing to private registries

4. **DEPLOYMENT_SSH_KEY**
   - Description: SSH key for deployment to production servers
   - Add public key to target server's authorized_keys

## Setting Secrets in GitHub

1. Navigate to your repository
2. Go to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add name and value for each secret

## Docker Secrets

For production deployment, use Docker Swarm mode with encrypted secrets:

```bash
# Create encrypted secrets
echo "your-secret-value" | docker secret create secret_name -

# Use in docker-compose.yml
secrets:
  - secret_name
```

## Environment Variables in Containers

All sensitive configuration should be passed via environment variables:

```yaml
services:
  agent:
    environment:
      - GITHUB_TOKEN=${GITHUB_TOKEN}
      - LLM_API_KEY=${LLM_API_KEY}
```

Never commit secrets to version control. Use `.env.example` as a template and add `.env` to `.gitignore`.
