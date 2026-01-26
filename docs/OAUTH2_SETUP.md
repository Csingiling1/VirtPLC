# OAuth2 Authentication Setup Guide

This guide explains how to configure OAuth2 authentication for Google, Microsoft, and Ignition providers in the VirtPLC application.

## Prerequisites

- Google Cloud Console account (for Google OAuth2)
- Microsoft Azure account (for Microsoft OAuth2)
- Ignition Gateway access (for Ignition OAuth2)
- Environment variables configured in your deployment

## Google OAuth2 Setup

### 1. Create Google OAuth2 Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API" and enable it
4. Create OAuth2 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Add authorized redirect URIs:
     - `http://localhost:8080/login/oauth2/code/google` (for local development)
     - `https://yourdomain.com/login/oauth2/code/google` (for production)
5. Copy the Client ID and Client Secret

### 2. Configure Environment Variables

Add these to your environment or `.env` file:

```bash
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
```

## Microsoft OAuth2 Setup

### 1. Create Microsoft OAuth2 App

1. Go to the [Azure Portal](https://portal.azure.com/)
2. Navigate to "Azure Active Directory" > "App registrations"
3. Click "New registration"
4. Configure:
   - Name: "VirtPLC"
   - Supported account types: "Accounts in any organizational directory"
   - Redirect URI: `http://localhost:8080/login/oauth2/code/microsoft` (Web)
5. Copy the Application (client) ID

### 2. Create Client Secret

1. In your app registration, go to "Certificates & secrets"
2. Click "New client secret"
3. Add a description and set expiration
4. Copy the secret value immediately

### 3. Configure Environment Variables

```bash
MICROSOFT_CLIENT_ID=your_microsoft_client_id_here
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret_here
```

## Ignition OAuth2 Setup

### 1. Configure Ignition Gateway

1. Access your Ignition Gateway web interface
2. Go to Config > Security > Identity Providers
3. Create a new OAuth2 provider or use existing one
4. Configure the provider settings:
   - Client ID: Generate or use existing
   - Client Secret: Generate or use existing
   - Authorization Endpoint: Your Ignition OAuth2 endpoint
   - Token Endpoint: Your Ignition token endpoint
   - User Info Endpoint: Your Ignition user info endpoint
5. Set redirect URI: `http://localhost:8080/login/oauth2/code/ignition`

### 2. Configure Environment Variables

```bash
IGNITION_CLIENT_ID=your_ignition_client_id_here
IGNITION_CLIENT_SECRET=your_ignition_client_secret_here
```

## Application Configuration

The OAuth2 configuration is already set up in `application.yml`. The application will automatically use the environment variables for client credentials.

## Testing OAuth2 Login

1. Start the application
2. Navigate to the login page
3. Click on the OAuth2 provider button (Google, Microsoft, or Ignition)
4. Complete the OAuth2 flow
5. Verify that you are logged in and a user account is created

## Troubleshooting

### Common Issues

1. **Invalid redirect URI**: Ensure the redirect URIs match exactly in both the provider console and application.yml
2. **Client credentials not found**: Check that environment variables are set correctly
3. **CORS issues**: Ensure CORS is configured to allow the OAuth2 provider domains
4. **User creation fails**: Check database connectivity and user table schema

### Debug Logging

Enable debug logging for OAuth2:

```yaml
logging:
  level:
    org.springframework.security: DEBUG
    org.springframework.web: DEBUG
```

## Security Considerations

- Always use HTTPS in production
- Store client secrets securely (environment variables, not in code)
- Regularly rotate client secrets
- Limit redirect URIs to trusted domains only
- Monitor OAuth2 login attempts for suspicious activity

## Frontend Integration

The frontend should include OAuth2 login buttons that redirect to:

- `/oauth2/authorization/google`
- `/oauth2/authorization/microsoft`
- `/oauth2/authorization/ignition`

After successful authentication, users will be redirected to `/api/auth/oauth2/success` which handles user creation and JWT token generation.