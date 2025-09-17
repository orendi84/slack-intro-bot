# GitHub MCP Server Setup Guide

## Step 1: Create GitHub Personal Access Token

1. **Go to GitHub Settings**: https://github.com/settings/tokens
2. **Click "Generate new token"** → "Generate new token (classic)"
3. **Configure token**:
   - **Note**: "Claude Code MCP Server"
   - **Expiration**: Choose your preference (90 days recommended)
   - **Scopes**: Select these permissions:
     - `repo` (Full control of private repositories)
     - `public_repo` (Access public repositories)
     - `read:org` (Read org membership)
     - `read:user` (Read user profile data)

4. **Copy the token** (you won't see it again!)

## Step 2: Configure MCP Server with Your Token

```bash
# Remove the current server (with placeholder token)
claude mcp remove github

# Add server with your actual token
claude mcp add github -e GITHUB_PERSONAL_ACCESS_TOKEN=YOUR_ACTUAL_TOKEN_HERE -- docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server
```

## Step 3: Verify Connection

```bash
# Check if server is connected
claude mcp list

# Should show:
# github: docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server - ✓ Connected
```

## Step 4: Test MCP Server

Once configured with your real token, I'll be able to:
- Create repositories directly through MCP
- Set repository settings and descriptions
- Push code and manage branches
- Configure repository topics and metadata

## Alternative: Use GitHub CLI

If MCP server has issues, we can use GitHub CLI:
```bash
# Complete the authentication we started
gh auth login
# Use code: FB5A-2C6B at https://github.com/login/device

# Then create repo
gh repo create slack-intro-bot --public --description "Automated Slack introduction detection and welcome message generation"
```

## Security Note

⚠️ **Important**: Keep your GitHub token secure
- Never commit tokens to repositories
- Use token with minimal required permissions
- Consider using fine-grained tokens for better security
- Set reasonable expiration dates