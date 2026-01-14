# Security Guidelines for VirtPLC

## ⚠️ CRITICAL SECURITY CHANGES IMPLEMENTED

### 1. CORS Protection
- ✅ Removed wildcard `@CrossOrigin(origins = "*")` from all controllers
- ✅ Implemented strict CORS configuration with specific allowed origins
- ✅ Use origin patterns instead of wildcards in production
- ✅ Added CORS preflight caching (1 hour)

**Action Required for Production:**
Update `CorsConfig.java` with your actual production domain:
```java
configuration.setAllowedOriginPatterns(Arrays.asList(
    "https://yourdomain.com",
    "https://*.yourdomain.com"
));
```

### 2. Input Validation
- ✅ Added validation for device history endpoint:
  - Device ID: alphanumeric, underscore, hyphen only (max 100 chars)
  - Time range: validated and limited to 30 days max
  - Prevents SQL injection via path parameters

**Recommendation:** Add similar validation to all user input endpoints.

### 3. SQL Injection Prevention
- ✅ All queries use parameterized statements via `JdbcTemplate`
- ✅ No string concatenation in SQL queries
- ✅ Device ID validated with regex before database query

### 4. Nginx Security Enhancements
- ✅ Hide nginx version (`server_tokens off`)
- ✅ Buffer overflow protection
- ✅ Slowloris attack mitigation:
  - `client_body_timeout 12s`
  - `client_header_timeout 12s`
  - `send_timeout 10s`
- ✅ Request size limits:
  - `client_body_buffer_size 1K`
  - `client_header_buffer_size 1k`
  - `client_max_body_size 20M`
- ✅ HTTP method filtering (only GET, POST, PUT, DELETE, OPTIONS, PATCH)
- ✅ Block hidden files (`.env`, `.git`, etc.)
- ✅ Block sensitive file extensions (`.sql`, `.conf`, `.log`, etc.)
- ✅ Prevent directory listing

### 5. Security Headers
Added comprehensive security headers:
- ✅ `X-Frame-Options: SAMEORIGIN` (prevent clickjacking)
- ✅ `X-Content-Type-Options: nosniff` (prevent MIME sniffing)
- ✅ `X-XSS-Protection: 1; mode=block` (XSS protection)
- ✅ `Content-Security-Policy` (restrict resource loading)
- ✅ `Strict-Transport-Security` (enforce HTTPS)
- ✅ `Permissions-Policy` (disable dangerous features)
- ✅ `Referrer-Policy: strict-origin-when-cross-origin`

### 6. Rate Limiting (DDoS Protection)
- ✅ API endpoints: 10 req/s (burst 20)
- ✅ Data endpoints: 5 req/s (burst 10)
- ✅ Static content: 100 req/s (burst 20)
- ✅ Connection limit: 10 concurrent per IP

### 7. Spring Security Configuration
- ✅ Security headers configured in Spring Security
- ✅ HSTS enabled (1 year max-age)
- ✅ Frame options set to SAMEORIGIN
- ✅ XSS protection enabled

## 🔒 PRODUCTION DEPLOYMENT CHECKLIST

### Environment Variables (CRITICAL)
Never use default values in production! Update these in `.env`:

```bash
# Database Passwords - CHANGE THESE
POSTGRES_PASSWORD=<strong-random-password>
TIMESCALE_PASSWORD=<strong-random-password>

# JWT Secret - CHANGE THIS
JWT_SECRET=<generate-using: openssl rand -base64 64>

# MQTT Password - CHANGE THIS
MQTT_PASSWORD=<strong-random-password>

# Node-RED Credentials - CHANGE THIS
NODE_RED_CREDENTIAL_SECRET=<generate-using: openssl rand -base64 32>

# Ignition Gateway - CHANGE THIS
GATEWAY_ADMIN_PASSWORD=<strong-admin-password>
```

### SSL/TLS Configuration
Current setup uses HTTP only. For production:

1. Obtain SSL certificate (Let's Encrypt recommended)
2. Update `nginx/nginx.conf`:
```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
}

server {
    listen 80;
    return 301 https://$server_name$request_uri;
}
```

### Database Security
1. ✅ Use parameterized queries (already implemented)
2. ⚠️ Create separate database users with minimal privileges
3. ⚠️ Enable PostgreSQL SSL connections
4. ⚠️ Restrict database access to application network only

### Network Security
1. ⚠️ Use Docker network isolation (partially implemented)
2. ⚠️ Expose only nginx on public interface
3. ⚠️ Use firewall rules to restrict access
4. ⚠️ Consider using VPN for admin access

### Monitoring & Logging
1. ✅ Access logs enabled in nginx
2. ⚠️ Set up log aggregation (ELK stack recommended)
3. ⚠️ Monitor for suspicious patterns:
   - Multiple 429 responses (rate limit hits)
   - 401/403 patterns (authentication failures)
   - SQL injection attempts in logs
4. ⚠️ Set up alerts for security events

### Authentication & Authorization
1. ✅ JWT-based authentication implemented
2. ✅ Stateless session management
3. ⚠️ Implement JWT token rotation
4. ⚠️ Add token expiration (recommended: 15 minutes)
5. ⚠️ Implement refresh tokens
6. ⚠️ Add multi-factor authentication (MFA)

### API Security
1. ✅ Rate limiting configured
2. ✅ Input validation on critical endpoints
3. ⚠️ Implement API versioning
4. ⚠️ Add request signing for sensitive operations
5. ⚠️ Implement API key rotation mechanism

### Container Security
1. ⚠️ Run containers as non-root user
2. ⚠️ Use minimal base images
3. ⚠️ Regular security updates:
   ```bash
   docker-compose pull
   docker-compose up -d --build
   ```
4. ⚠️ Scan images for vulnerabilities:
   ```bash
   docker scan virtplc-backend
   ```

### File Upload Security
If implementing file uploads:
1. Validate file types strictly
2. Limit file sizes
3. Scan for malware
4. Store outside webroot
5. Generate random filenames

### Redis Security
1. ⚠️ Add Redis password authentication
2. ⚠️ Use Redis ACLs
3. ⚠️ Encrypt Redis connections
4. ⚠️ Limit Redis access to backend only

## 🛡️ Security Testing

### Recommended Tools
1. **OWASP ZAP** - Automated security testing
2. **Burp Suite** - Manual penetration testing
3. **sqlmap** - SQL injection testing (should fail)
4. **nikto** - Web server scanner
5. **nmap** - Network security scanner

### Test Commands
```bash
# Test rate limiting
for i in {1..30}; do curl -w "\n" http://localhost/api/data/hierarchical-live; done

# Test SQL injection (should be blocked)
curl "http://localhost/api/data/device/'; DROP TABLE plc_data; --/history?startTime=0&endTime=1"

# Test XSS (should be sanitized)
curl "http://localhost/api/data/device/<script>alert(1)</script>/history?startTime=0&endTime=1"

# Test header injection
curl -H "X-Forwarded-For: <script>alert(1)</script>" http://localhost/health
```

## 📋 Security Audit Log

### 2026-01-06: Security Hardening Implemented
- Removed wildcard CORS from all controllers
- Added input validation for device history endpoint
- Enhanced nginx security (Slowloris protection, buffer limits)
- Added comprehensive security headers
- Restricted CORS to specific origin patterns
- Added file access restrictions
- Implemented HTTP method filtering
- Added Spring Security headers configuration

### Next Steps (Priority Order)
1. **HIGH**: Update all production passwords/secrets
2. **HIGH**: Implement SSL/TLS
3. **HIGH**: Add JWT token expiration/rotation
4. **MEDIUM**: Database user privilege separation
5. **MEDIUM**: Implement request logging and monitoring
6. **MEDIUM**: Add container security scanning
7. **LOW**: Implement MFA for admin users
8. **LOW**: Add API versioning

## 🚨 Known Limitations

1. **CSRF Protection**: Disabled for stateless JWT API. Consider enabling for cookie-based sessions if implemented.
2. **dangerouslySetInnerHTML**: Used in `chart.tsx` for CSS injection - content is controlled (not user input).
3. **Password Storage**: Ensure strong hashing (bcrypt with high cost factor).
4. **Session Management**: Stateless JWT - ensure short expiration times.

## 📞 Security Contacts

Report security vulnerabilities to: [security contact email]

Never commit:
- Passwords or secrets
- API keys
- SSL private keys
- `.env` files with real credentials

Use `.env.example` as template only.
