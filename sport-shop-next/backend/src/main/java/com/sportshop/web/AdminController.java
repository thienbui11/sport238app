package com.sportshop.web;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.sportshop.config.ShopProperties;
import com.sportshop.service.CatalogService;
import com.sportshop.service.ConfigService;
import com.sportshop.service.ExcelImportService;
import com.sportshop.service.ImageStorageService;
import com.sportshop.service.SapoParser;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContext;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.context.HttpSessionSecurityContextRepository;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

@RestController
public class AdminController {
    public record LoginRequest(String password) {}
    public record ProductInfoRequest(@JsonProperty("display_title") String displayTitle, String description, boolean hidden, boolean featured, String category) {}
    public record ImagesRequest(@JsonProperty("product_id") String productId, String color, List<String> urls) {}

    private static final int MAX_FAILS = 5;
    private static final long WINDOW_MS = 10 * 60_000L;

    private final ShopProperties props;
    private final CatalogService catalog;
    private final ConfigService config;
    private final ExcelImportService excel;
    private final ImageStorageService images;
    private final Map<String, long[]> fails = new ConcurrentHashMap<>();   // ip -> {số lần sai, thời điểm bắt đầu}

    public AdminController(ShopProperties props, CatalogService catalog, ConfigService config,
                           ExcelImportService excel, ImageStorageService images) {
        this.props = props; this.catalog = catalog; this.config = config; this.excel = excel; this.images = images;
    }

    @PostMapping("/api/admin/login")
    ResponseEntity<Map<String, Object>> login(@RequestBody LoginRequest body, HttpServletRequest req, HttpServletResponse res) {
        String ip = req.getRemoteAddr();
        long now = System.currentTimeMillis();
        long[] f = fails.compute(ip, (k, v) -> (v == null || now - v[1] > WINDOW_MS) ? new long[]{0, now} : v);
        if (f[0] >= MAX_FAILS) return ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).body(Map.of("error", "too_many_attempts"));
        if (body.password() == null || !sameSecret(body.password(), props.adminPassword())) {
            f[0]++;
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(Map.of("error", "wrong_password"));
        }
        fails.remove(ip);
        if (req.getSession(false) != null) req.changeSessionId();   // chống session fixation
        var auth = UsernamePasswordAuthenticationToken.authenticated("admin", null, List.of(new SimpleGrantedAuthority("ROLE_ADMIN")));
        SecurityContext ctx = SecurityContextHolder.createEmptyContext();
        ctx.setAuthentication(auth);
        SecurityContextHolder.setContext(ctx);
        new HttpSessionSecurityContextRepository().saveContext(ctx, req, res);
        return ResponseEntity.ok(Map.of("ok", true));
    }

    @PostMapping("/api/admin/logout")
    Map<String, Object> logout(HttpServletRequest req) {
        HttpSession s = req.getSession(false);
        if (s != null) s.invalidate();
        SecurityContextHolder.clearContext();
        return Map.of("ok", true);
    }

    @GetMapping("/api/admin/me")
    Map<String, Object> me() { return Map.of("ok", true); }   // vào được đây nghĩa là đã đăng nhập

    @GetMapping("/api/admin/products")
    CatalogService.Catalog adminProducts() { return catalog.catalog(true); }

    @PostMapping(value = "/api/admin/import", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    Map<String, Object> importExcel(@RequestParam("file") MultipartFile file) throws IOException {
        String name = file.getOriginalFilename() == null ? "" : file.getOriginalFilename().toLowerCase();
        if (file.isEmpty() || !name.endsWith(".xlsx")) throw new BadRequestException("need_xlsx_file");
        SapoParser.Result parsed = SapoParser.parse(excel.read(file.getInputStream()));
        Map<String, Integer> done = catalog.importProducts(parsed.products());
        Map<String, Object> out = new HashMap<>(done);
        out.put("productsInFile", parsed.totalProductsInFile());
        out.put("droppedZeroPrice", parsed.droppedZeroPrice());
        return out;
    }

    @PutMapping("/api/admin/products/{id}")
    ResponseEntity<Map<String, Object>> updateProduct(@PathVariable String id, @RequestBody ProductInfoRequest body) {
        boolean ok = catalog.updateInfo(id, body.displayTitle(), body.description(), body.hidden(), body.featured(), body.category());
        return ok ? ResponseEntity.ok(Map.of("ok", true))
                  : ResponseEntity.status(HttpStatus.NOT_FOUND).body(Map.of("error", "not_found"));
    }

    @PostMapping("/api/admin/images")
    Map<String, Object> setImages(@RequestBody ImagesRequest body) {
        if (body.productId() == null || body.productId().isBlank()) throw new BadRequestException("missing_product_id");
        catalog.setImages(body.productId(), body.color() == null ? "" : body.color(), body.urls() == null ? List.of() : body.urls());
        return Map.of("ok", true);
    }

    @PostMapping("/api/admin/config")
    Map<String, Object> setConfig(@RequestBody Map<String, String> body) {
        config.set(body);
        return Map.of("ok", true);
    }

    /** Tải ảnh lên: gửi thẳng nội dung tệp làm body (không cần multipart). */
    @PostMapping(value = "/api/admin/upload", consumes = MediaType.ALL_VALUE)
    Map<String, String> upload(@RequestBody byte[] data) {
        return Map.of("url", images.save(data));
    }

    private static boolean sameSecret(String a, String b) {
        return MessageDigest.isEqual(a.getBytes(StandardCharsets.UTF_8), b.getBytes(StandardCharsets.UTF_8));
    }
}
