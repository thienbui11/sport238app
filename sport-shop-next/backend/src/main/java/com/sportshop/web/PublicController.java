package com.sportshop.web;

import com.sportshop.service.CatalogService;
import com.sportshop.service.ConfigService;
import java.time.Duration;
import java.util.Map;
import org.springframework.http.CacheControl;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class PublicController {
    private final CatalogService catalog;
    private final ConfigService config;

    public PublicController(CatalogService catalog, ConfigService config) { this.catalog = catalog; this.config = config; }

    @GetMapping("/api/products")
    ResponseEntity<CatalogService.Catalog> products() {
        return ResponseEntity.ok().cacheControl(CacheControl.maxAge(Duration.ofSeconds(30)).cachePublic()).body(catalog.catalog(false));
    }

    @GetMapping("/api/config")
    Map<String, String> config() { return config.get(); }
}
