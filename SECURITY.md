# Security Guidelines for Slack Intro Bot

## 🔒 Security Best Practices

### Environment Variables & Secrets Management

**✅ DO:**
- Store all sensitive data in `.env` file (gitignored)
- Use strong, unique API tokens
- Regularly rotate API keys and tokens
- Limit bot permissions to minimum required
- Review and audit access logs regularly

**❌ DON'T:**
- Never commit `.env` file to version control
- Never hardcode secrets in source code
- Never share tokens in chat/email
- Never use production tokens for testing
- Never store secrets in plain text files

### File Permissions

```bash
# Set secure permissions for sensitive files
chmod 600 .env                    # Owner read/write only
chmod 600 config.py               # Protect config file
chmod 700 welcome_messages/       # Secure output directory
```

### API Token Security

#### Slack Bot Token Permissions
Only grant these minimal permissions:
- `channels:read` - Read channel information
- `channels:history` - Read channel messages
- `users:read` - Read user profile information

#### Token Storage
```bash
# Example .env structure
SLACK_BOT_TOKEN=xoxb-xxxx-xxxx-xxxx    # Bot User OAuth Token
SLACK_APP_TOKEN=xapp-xxxx-xxxx-xxxx    # App-Level Token (if needed)
```

### Network Security

- Use HTTPS for all API endpoints
- Validate webhook signatures if using webhooks
- Implement rate limiting for API calls
- Monitor for unusual API usage patterns

### Data Privacy

#### Personal Information Handling
- **LinkedIn URLs**: Store only for immediate processing, delete after use
- **User Names**: Handle according to your privacy policy
- **Message Content**: Process locally, avoid cloud storage of raw messages
- **Logs**: Sanitize logs to remove personal information

#### Data Retention
```python
# Example: Clear old data after processing
def cleanup_old_data():
    # Remove files older than 30 days
    cutoff_date = datetime.now() - timedelta(days=30)
    # Implementation here
```

### Deployment Security

#### Production Environment
```bash
# Use systemd service with restricted user
sudo useradd --system --no-create-home slack-bot
sudo chown slack-bot:slack-bot /path/to/bot/
```

#### Cron Job Security
```bash
# Use dedicated user for cron jobs
# Add to slack-bot user's crontab
sudo -u slack-bot crontab -e
0 8 * * * cd /home/slack-bot && python3 slack_intro_cron.py
```

### Monitoring & Alerting

#### Security Monitoring
- Monitor for failed authentication attempts
- Track unusual API usage patterns
- Set up alerts for configuration changes
- Log all bot activities with timestamps

#### Example Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('slack_bot_security.log'),
        logging.StreamHandler()
    ]
)
```

### Incident Response

#### In Case of Token Compromise:
1. **Immediately revoke** the compromised token in Slack Admin
2. **Generate new token** with same permissions
3. **Update .env file** with new token
4. **Review logs** for any unauthorized access
5. **Notify relevant stakeholders**

#### Emergency Contacts
- Slack Workspace Admin: [contact info]
- Security Team: [contact info]
- IT Support: [contact info]

### Compliance Considerations

#### GDPR/Privacy Compliance
- Document what personal data is processed
- Implement data subject rights (deletion, access)
- Maintain records of processing activities
- Ensure lawful basis for processing

#### Corporate Policies
- Follow company data handling policies
- Comply with information security standards
- Document security controls implemented
- Regular security reviews and updates

### Configuration Validation

```python
# Example security checks in config.py
def validate_security_settings():
    # Check file permissions
    env_stat = os.stat('.env')
    if env_stat.st_mode & 0o077:
        print("⚠️  WARNING: .env file has overly permissive permissions")

    # Validate token format
    if config.slack_bot_token and not config.slack_bot_token.startswith('xoxb-'):
        print("⚠️  WARNING: Invalid Slack bot token format")
```

### Regular Security Tasks

#### Weekly
- [ ] Review bot activity logs
- [ ] Check for unauthorized API calls
- [ ] Verify file permissions

#### Monthly
- [ ] Rotate API tokens
- [ ] Review user permissions
- [ ] Update dependencies
- [ ] Security patch review

#### Quarterly
- [ ] Full security audit
- [ ] Penetration testing
- [ ] Update security documentation
- [ ] Train team on security practices

### Emergency Shutdown

```bash
# Quick disable commands
pkill -f slack_intro_bot         # Stop running processes
crontab -r                      # Remove cron jobs
chmod 000 .env                  # Disable access to secrets
```

## 🛡️ Security Checklist

- [ ] `.env` file created and gitignored
- [ ] File permissions set correctly (600 for .env)
- [ ] API tokens have minimal required permissions
- [ ] Logging implemented for security events
- [ ] Data retention policy defined
- [ ] Incident response plan documented
- [ ] Regular security review scheduled
- [ ] Team trained on security practices

## 📞 Security Contact

For security issues or questions:
- **Email**: [security contact]
- **Slack**: [security channel]
- **Emergency**: [emergency contact]

---

**Remember**: Security is everyone's responsibility. When in doubt, choose the more secure option.