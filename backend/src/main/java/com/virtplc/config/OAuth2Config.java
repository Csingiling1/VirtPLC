package com.virtplc.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Conditional;
import org.springframework.boot.autoconfigure.condition.ConditionalOnExpression;
import org.springframework.security.oauth2.client.registration.ClientRegistration;
import org.springframework.security.oauth2.client.registration.ClientRegistrationRepository;
import org.springframework.security.oauth2.client.registration.InMemoryClientRegistrationRepository;
import org.springframework.security.oauth2.core.AuthorizationGrantType;
import org.springframework.security.oauth2.core.ClientAuthenticationMethod;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.util.StringUtils;

import java.util.ArrayList;
import java.util.List;

@Configuration
public class OAuth2Config {

    @Value("${spring.security.oauth2.client.registration.google.client-id:}")
    private String googleClientId;

    @Value("${spring.security.oauth2.client.registration.google.client-secret:}")
    private String googleClientSecret;

    @Value("${spring.security.oauth2.client.registration.microsoft.client-id:}")
    private String microsoftClientId;

    @Value("${spring.security.oauth2.client.registration.microsoft.client-secret:}")
    private String microsoftClientSecret;

    @Value("${spring.security.oauth2.client.registration.ignition.client-id:}")
    private String ignitionClientId;

    @Value("${spring.security.oauth2.client.registration.ignition.client-secret:}")
    private String ignitionClientSecret;

    @Bean
    @ConditionalOnExpression("${spring.security.oauth2.client.registration.google.client-id:''}.length() > 0 or ${spring.security.oauth2.client.registration.microsoft.client-id:''}.length() > 0 or ${spring.security.oauth2.client.registration.ignition.client-id:''}.length() > 0")
    public ClientRegistrationRepository clientRegistrationRepository() {
        List<ClientRegistration> registrations = new ArrayList<>();

        if (StringUtils.hasText(googleClientId)) {
            registrations.add(googleClientRegistration());
        }
        if (StringUtils.hasText(microsoftClientId)) {
            registrations.add(microsoftClientRegistration());
        }
        if (StringUtils.hasText(ignitionClientId)) {
            registrations.add(ignitionClientRegistration());
        }

        return new InMemoryClientRegistrationRepository(registrations);
    }

    private ClientRegistration googleClientRegistration() {
        return ClientRegistration.withRegistrationId("google")
                .clientId(googleClientId)
                .clientSecret(googleClientSecret)
                .clientAuthenticationMethod(ClientAuthenticationMethod.CLIENT_SECRET_BASIC)
                .authorizationGrantType(AuthorizationGrantType.AUTHORIZATION_CODE)
                .redirectUri("{baseUrl}/login/oauth2/code/{registrationId}")
                .scope("openid", "email", "profile")
                .authorizationUri("https://accounts.google.com/o/oauth2/auth")
                .tokenUri("https://oauth2.googleapis.com/token")
                .userInfoUri("https://www.googleapis.com/oauth2/v2/userinfo")
                .userNameAttributeName("email")
                .jwkSetUri("https://www.googleapis.com/oauth2/v3/certs")
                .clientName("Google")
                .build();
    }

    private ClientRegistration microsoftClientRegistration() {
        return ClientRegistration.withRegistrationId("microsoft")
                .clientId(microsoftClientId)
                .clientSecret(microsoftClientSecret)
                .clientAuthenticationMethod(ClientAuthenticationMethod.CLIENT_SECRET_BASIC)
                .authorizationGrantType(AuthorizationGrantType.AUTHORIZATION_CODE)
                .redirectUri("{baseUrl}/login/oauth2/code/{registrationId}")
                .scope("openid", "email", "profile")
                .authorizationUri("https://login.microsoftonline.com/common/oauth2/v2.0/authorize")
                .tokenUri("https://login.microsoftonline.com/common/oauth2/v2.0/token")
                .userInfoUri("https://graph.microsoft.com/oidc/userinfo")
                .userNameAttributeName("email")
                .jwkSetUri("https://login.microsoftonline.com/common/discovery/v2.0/keys")
                .clientName("Microsoft")
                .build();
    }

    private ClientRegistration ignitionClientRegistration() {
        return ClientRegistration.withRegistrationId("ignition")
                .clientId(ignitionClientId)
                .clientSecret(ignitionClientSecret)
                .clientAuthenticationMethod(ClientAuthenticationMethod.CLIENT_SECRET_BASIC)
                .authorizationGrantType(AuthorizationGrantType.AUTHORIZATION_CODE)
                .redirectUri("{baseUrl}/login/oauth2/code/{registrationId}")
                .scope("openid", "email", "profile")
                .authorizationUri("https://accounts.ignitionapp.com/oauth/authorize")
                .tokenUri("https://accounts.ignitionapp.com/oauth/token")
                .userInfoUri("https://accounts.ignitionapp.com/oauth/userinfo")
                .userNameAttributeName("email")
                .jwkSetUri("https://accounts.ignitionapp.com/oauth/jwks")
                .clientName("Ignition")
                .build();
    }
}