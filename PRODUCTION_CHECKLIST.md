# Production Deployment Checklist

Use this checklist before deploying to production to ensure everything is ready.

## Security & Configuration

- [ ] `FLASK_ENV` is set to `production`
- [ ] `SECRET_KEY` is set to a secure, random string (minimum 32 characters)
- [ ] `.env` file is NOT committed to git (check `.gitignore`)
- [ ] All secrets are in environment variables, not in code
- [ ] Database credentials are strong (20+ characters)
- [ ] SMTP credentials are verified and functional
- [ ] SSL/TLS certificate obtained and configured
- [ ] HTTPS is enforced (redirect HTTP to HTTPS)

## Application

- [ ] Debug mode is disabled (`FLASK_ENV=production`)
- [ ] All dependencies installed from `requirements.txt`
- [ ] Application tested locally with production settings
- [ ] Logging is configured and enabled
- [ ] Error tracking (Sentry) configured (optional)
- [ ] No hardcoded URLs or configuration values
- [ ] CORS is properly configured for production domain
- [ ] Rate limiting implemented on API endpoints

## Database

- [ ] Database server is production-grade (managed or secure VPS)
- [ ] Database is initialized with all tables (`python db_setup.py`)
- [ ] Database backups are configured and tested
- [ ] Database user has minimal required permissions
- [ ] Database connections use SSL/TLS
- [ ] Database firewall rules restrict access to app server only
- [ ] Database performance has been optimized
- [ ] Connection pooling configured

## Infrastructure

- [ ] Web server (Nginx/Apache) configured
- [ ] Reverse proxy properly configured (if applicable)
- [ ] SSL certificate installed and valid
- [ ] Firewall rules properly configured
- [ ] DDoS protection enabled (Cloudflare/AWS Shield)
- [ ] Monitoring and alerting configured
- [ ] Automated backups scheduled and tested
- [ ] Disaster recovery plan documented

## Email Configuration

- [ ] SMTP server is production-grade (dedicated or managed service)
- [ ] SMTP credentials are correct and app can authenticate
- [ ] SMTP uses TLS/SSL for secure connections
- [ ] Email validation is enabled
- [ ] Bounce handling is configured
- [ ] Sender reputation monitoring enabled
- [ ] SPF, DKIM, DMARC records configured for domain
- [ ] Unsubscribe mechanism implemented

## Deployment & Operations

- [ ] Deployment process documented
- [ ] Rollback procedure documented
- [ ] Application startup verified
- [ ] Health check endpoint is working
- [ ] Logs are being written and monitored
- [ ] Performance monitoring enabled
- [ ] Alerting configured for critical errors
- [ ] On-call rotation established

## Testing

- [ ] All tests pass in production environment
- [ ] Load testing completed
- [ ] Database failover tested
- [ ] Email sending tested with test accounts
- [ ] User authentication tested
- [ ] API endpoints tested
- [ ] Error handling verified
- [ ] Backup restoration tested

## Documentation

- [ ] Deployment guide reviewed and accessible
- [ ] Runbook for common issues documented
- [ ] API documentation up to date
- [ ] Database schema documented
- [ ] Environment variables documented
- [ ] Monitoring dashboard accessible
- [ ] Emergency contacts documented
- [ ] Escalation procedures documented

## Monitoring & Maintenance

- [ ] Application uptime monitor configured
- [ ] Error rate monitoring enabled
- [ ] Database performance monitoring enabled
- [ ] Email delivery monitoring enabled
- [ ] Security monitoring active
- [ ] Log aggregation configured
- [ ] Performance metrics tracked
- [ ] Regular maintenance schedule established

## Post-Deployment

- [ ] Smoke tests on production passed
- [ ] Real user testing conducted
- [ ] Monitoring dashboards active
- [ ] Team notified of deployment
- [ ] Runbook shared with ops team
- [ ] Performance baseline established
- [ ] First 24 hours monitored closely
- [ ] Any issues logged and addressed

---

## Final Sign-Off

| Role | Name | Date | Notes |
|------|------|------|-------|
| Developer | | | |
| DevOps | | | |
| QA | | | |
| Product Manager | | | |

---

## Quick Command Reference

```bash
# Generate secure SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Test database connection
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -e "SELECT 1;"

# Test SMTP connection
python3 -c "import smtplib; s=smtplib.SMTP('$SMTP_HOST',$SMTP_PORT); s.starttls(); s.login('$SMTP_USERNAME','$SMTP_PASSWORD'); print('✓ SMTP OK')"

# Initialize database
python db_setup.py

# Run application locally for testing
FLASK_ENV=production python dashboard.py

# Build and test Docker image
docker build -t email-system:latest .
docker run -p 5001:5001 email-system:latest

# Deploy with Gunicorn
gunicorn wsgi:app --workers 4 --bind 0.0.0.0:5001
```

---

## Support

For deployment assistance, refer to:
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Detailed deployment instructions
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions
- [README.md](README.md) - General documentation
