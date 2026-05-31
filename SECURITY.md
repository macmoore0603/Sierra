# Security Policy for Sierra

## Overview

Sierra is a personal AI assistant with deep access to your system, personal data, and integrations. Security and privacy are paramount.

## Data Handling & Privacy

### What Sierra Accesses
- **System Level**: With God Mode enabled, Sierra can access:
  - Calendar and email (when integrated)
  - File system (for task execution)
  - System automation (AppleScript on macOS)
  - Camera and audio (for gestures and voice)

### Data Processing
- Audio is processed in real-time by Google's Gemini API
- Memory and context are stored locally in your machine
- Personal integrations (Calendar, GitHub) store credentials securely
- No data is collected for analytics without explicit consent

### Local-First Architecture
- Intent classification uses on-device FunctionGemma
- Memory storage is local to your machine
- Sensitive operations require confirmation (unless God Mode)

## Security Best Practices

### Installation & Permissions
1. **Only use the official production build**: `/Applications/Sierra.app`
2. **Activate permissions explicitly**: Use the "ACTIVATE ALL PERMISSIONS" button
3. **Review permission requests**: Understand what each permission enables
4. **Use macOS Privacy settings**: Monitor what Sierra accesses

### API Keys & Credentials
- **Google Gemini API Key**: Store in `.env` file (never commit)
- **Integration Credentials**: Stored securely in system keychain where possible
- **OAuth Tokens**: Use secure token storage mechanisms

### Safe Practices
- Keep your `.env` file private (included in `.gitignore`)
- Never share API keys or credentials
- Review integration permissions regularly
- Update Sierra regularly for security patches

## God Mode Security Considerations

God Mode grants pervasive access with relaxed confirmations. Use responsibly:

### Access Levels
- **Voice (Hey Sierra)**: Full command execution
- **Gestures**: Hand tracking with system control
- **Face Auth**: Presence and biometric security
- **System Automation**: AppleScript-equivalent access
- **Personal Data**: Calendar, email, GitHub access

### Risk Mitigation
1. **Physical Security**: Keep your machine secure
2. **Network Security**: Use VPN and trusted networks
3. **Regular Audits**: Review command history and actions
4. **Controlled Access**: Disable God Mode features you don't need
5. **Logging**: Check memory logs for unexpected actions

## Reporting Security Issues

If you discover a security vulnerability:

1. **Do NOT open a public issue**
2. **Email**: macmoore0603@github or use GitHub's private security advisory
3. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)

4. **Timeline**: We'll acknowledge within 48 hours
5. **Resolution**: We aim to address critical issues within 7 days

## Dependency Security

### Python Dependencies
```bash
# Check for known vulnerabilities
pip audit

# Update dependencies regularly
pip install --upgrade -r requirements.txt
```

### Node Dependencies
```bash
# Check for vulnerabilities
npm audit

# Fix automatically where possible
npm audit fix
```

## Compliance & Legal

- **License**: MIT License (see LICENSE file)
- **No Warranty**: Provided as-is without warranty
- **Your Responsibility**: You are responsible for how you use Sierra
- **Local Data**: You own all data stored locally on your machine

## Security Updates

- We follow semantic versioning
- Security patches are released as patch versions (e.g., 1.0.1)
- Major security issues trigger immediate releases
- Subscribe to releases for notifications

## Third-Party Services

### Google Gemini API
- Terms: https://ai.google.dev/terms
- Privacy: Subject to Google's privacy policies
- Your responsibility to review and accept their terms

### Integrated Services (Optional)
- Calendar: Via OAuth 2.0 integration
- GitHub: Via personal access tokens
- Others: Configured per user preferences

## Regular Audits

Recommended security practices:

```bash
# Monthly: Update dependencies
pip install --upgrade -r requirements.txt
npm update

# Monthly: Check for vulnerabilities
pip audit
npm audit

# Quarterly: Review integrations and permissions
# In Settings → macOS Privacy & Security

# Quarterly: Check memory logs
# In Settings → Activity & History
```

## Questions?

For security questions or concerns:
- Check existing discussions
- Open a private discussion if urgent
- Email for critical concerns

Your security and privacy matter. Thank you for using Sierra responsibly.
