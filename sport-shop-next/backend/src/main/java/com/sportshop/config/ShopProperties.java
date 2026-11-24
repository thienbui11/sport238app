package com.sportshop.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "shop")
public record ShopProperties(String adminPassword, String uploadDir, String shopName, String messengerUser, String zaloPhone) {
    public ShopProperties {
        if (adminPassword == null || adminPassword.isBlank()) adminPassword = "admin123";
        if (uploadDir == null || uploadDir.isBlank()) uploadDir = "./uploads";
    }
}
