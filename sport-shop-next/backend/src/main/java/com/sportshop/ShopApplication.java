package com.sportshop;

import com.sportshop.config.ShopProperties;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;
import org.springframework.context.annotation.Bean;

@SpringBootApplication
@ConfigurationPropertiesScan
public class ShopApplication {
    private static final Logger log = LoggerFactory.getLogger(ShopApplication.class);

    public static void main(String[] args) {
        SpringApplication.run(ShopApplication.class, args);
    }

    @Bean
    CommandLineRunner passwordWarning(ShopProperties props) {
        return args -> {
            if ("admin123".equals(props.adminPassword())) {
                log.warn("Chưa đặt ADMIN_PASSWORD, đang dùng mật khẩu mặc định 'admin123'. Hãy đổi trước khi đưa lên mạng!");
            }
        };
    }
}
