# Security Policy

## Supported Versions

This is a personal MVP project for Garmin well-being tracking. Security updates will be applied to:

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |
| < main  | :x:                |

## Reporting a Vulnerability

While this is a personal project, I take security seriously. If you discover a security vulnerability, please:

1. **DO NOT** create a public issue
2. Contact the repository owner directly through GitHub
3. Provide details about the vulnerability and steps to reproduce
4. Allow reasonable time for a fix before public disclosure

## Security Measures

This repository implements several security best practices:

- ✅ **No hardcoded secrets**: All sensitive data excluded via .gitignore
- ✅ **CodeQL scanning**: Automated security analysis on all PRs
- ✅ **Branch protection**: Required CI checks before merge
- ✅ **Dependency scanning**: GitHub's built-in security scanning enabled
- ✅ **No PII**: Personal health data stays on-device only

## Scope

This is a personal fitness tracking application that:
- Runs locally on Garmin devices
- Does NOT transmit data to external services
- Does NOT store personal health information in the repository
- Uses only device-local storage for user data

## Out of Scope

The following are explicitly NOT security concerns for this project:
- Multi-user authentication (single-user only)
- Network security (no network features)
- Cloud data protection (no cloud features)

## Disclaimer

This application is for personal wellness tracking only and is not medical software. 
It should not be used for medical diagnosis or treatment decisions.