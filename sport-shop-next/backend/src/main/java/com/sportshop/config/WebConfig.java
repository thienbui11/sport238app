package com.sportshop.config;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.Duration;
import org.springframework.http.CacheControl;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

/** Phục vụ ảnh đã tải lên tại /uploads/** */
@Configuration
public class WebConfig implements WebMvcConfigurer {
    private final Path uploadDir;

    public WebConfig(ShopProperties props) throws IOException {
        this.uploadDir = Path.of(props.uploadDir()).toAbsolutePath();
        Files.createDirectories(uploadDir);   // phải tồn tại trước khi đổi sang URI (để có dấu / ở cuối)
    }

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        registry.addResourceHandler("/uploads/**")
                .addResourceLocations(uploadDir.toUri().toString())
                .setCacheControl(CacheControl.maxAge(Duration.ofDays(1)).cachePublic());
    }
}
