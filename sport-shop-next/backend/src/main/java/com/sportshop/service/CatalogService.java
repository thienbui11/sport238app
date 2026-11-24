package com.sportshop.service;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.sportshop.web.BadRequestException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowCallbackHandler;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/** Toàn bộ truy vấn sản phẩm, phiên bản, ảnh. Tên trường JSON giữ nguyên như bản Node để giao diện dùng lại được. */
@Service
public class CatalogService {
    public record VariantDto(String id, String sku, String option1, String option2, long price,
                             @JsonProperty("inventory_quantity") int inventoryQuantity) {}
    /** category: danh mục đang dùng trên web (chọn tay nếu có, không thì tự động). */
    public record ProductDto(String id, String title, @JsonProperty("display_title") String displayTitle,
                             String description, @JsonProperty("product_type") String productType,
                             String vendor, String category, @JsonProperty("category_auto") String categoryAuto,
                             @JsonProperty("category_override") String categoryOverride,
                             boolean active, boolean hidden, boolean featured, List<VariantDto> variants) {}
    /** images: khóa "idSP" (ảnh chung) hoặc "idSP:Màu" (ảnh riêng theo màu) */
    public record Catalog(List<ProductDto> products, Map<String, List<String>> images) {}

    private static final Pattern URL_OK = Pattern.compile("^(/uploads/[\\w.-]+|https?://\\S+)$");
    private final JdbcTemplate jdbc;

    public CatalogService(JdbcTemplate jdbc) { this.jdbc = jdbc; }

    @Transactional(readOnly = true)
    public Catalog catalog(boolean all) {
        Map<String, List<VariantDto>> byProduct = new HashMap<>();
        jdbc.query("SELECT id, product_id, sku, option1, option2, price, stock FROM variants ORDER BY seq",
            (RowCallbackHandler) rs -> byProduct.computeIfAbsent(rs.getString("product_id"), k -> new ArrayList<>())
                .add(new VariantDto(rs.getString("id"), rs.getString("sku"), rs.getString("option1"),
                    rs.getString("option2"), rs.getLong("price"), rs.getInt("stock"))));

        List<ProductDto> products = jdbc.query(
            "SELECT id, title, display_title, description, product_type, vendor, category, category_override, active, hidden, featured FROM products "
                + (all ? "" : "WHERE active = TRUE AND hidden = FALSE ") + "ORDER BY seq",
            (rs, i) -> {
                String auto = rs.getString("category"), over = rs.getString("category_override");
                String effective = !over.isEmpty() ? over : !auto.isEmpty() ? auto : SapoParser.ACC;
                return new ProductDto(rs.getString("id"), rs.getString("title"), rs.getString("display_title"),
                    rs.getString("description"), rs.getString("product_type"), rs.getString("vendor"),
                    effective, auto, over, rs.getBoolean("active"), rs.getBoolean("hidden"), rs.getBoolean("featured"),
                    byProduct.getOrDefault(rs.getString("id"), List.of()));
            })
            .stream().filter(p -> !p.variants().isEmpty()).toList();

        Map<String, List<String>> images = new LinkedHashMap<>();
        jdbc.query("SELECT product_id, color, url FROM product_images ORDER BY pos, id",
            (RowCallbackHandler) rs -> {
                String color = rs.getString("color"), pid = rs.getString("product_id");
                images.computeIfAbsent(color.isEmpty() ? pid : pid + ":" + color, k -> new ArrayList<>()).add(rs.getString("url"));
            });
        return new Catalog(products, images);
    }

    /** Nhập danh sách từ Sapo. Giữ nguyên ảnh; sản phẩm không còn trong file sẽ bị ẩn (không xóa). */
    @Transactional
    public Map<String, Integer> importProducts(List<SapoParser.Product> list) {
        if (list.isEmpty()) throw new BadRequestException("no_products_to_import");   // tránh lỡ ẩn toàn bộ sản phẩm
        jdbc.update("UPDATE products SET active = FALSE");
        int nv = 0;
        for (SapoParser.Product p : list) {
            jdbc.update("""
                INSERT INTO products(id, title, product_type, vendor, category, active) VALUES (?, ?, ?, ?, ?, TRUE)
                ON CONFLICT (id) DO UPDATE SET title = EXCLUDED.title, product_type = EXCLUDED.product_type,
                  vendor = EXCLUDED.vendor, category = EXCLUDED.category, active = TRUE""", p.id(), p.title(), p.productType(), p.vendor(), p.category());
            jdbc.update("DELETE FROM variants WHERE product_id = ?", p.id());
            List<Object[]> batch = new ArrayList<>();
            for (SapoParser.Variant v : p.variants())
                batch.add(new Object[]{v.id(), p.id(), v.sku(), v.option1(), v.option2(), v.price(), v.stock()});
            jdbc.batchUpdate("""
                INSERT INTO variants(id, product_id, sku, option1, option2, price, stock) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (id) DO UPDATE SET product_id = EXCLUDED.product_id, sku = EXCLUDED.sku,
                  option1 = EXCLUDED.option1, option2 = EXCLUDED.option2, price = EXCLUDED.price, stock = EXCLUDED.stock""", batch);
            nv += p.variants().size();
        }
        return Map.of("products", list.size(), "variants", nv);
    }

    /** Sửa thông tin chỉ có trên web. Trả về false nếu không có sản phẩm này. */
    @Transactional
    public boolean updateInfo(String id, String displayTitle, String description, boolean hidden, boolean featured, String category) {
        String override = SapoParser.CATEGORIES.contains(category) ? category : "";   // để trống = tự động theo tên
        return jdbc.update("UPDATE products SET display_title = ?, description = ?, hidden = ?, featured = ?, category_override = ? WHERE id = ?",
            clip(displayTitle, 200), clip(description, 4000), hidden, featured, override, id) > 0;
    }

    private static String clip(String s, int max) {
        if (s == null) return "";
        s = s.strip();
        return s.length() > max ? s.substring(0, max) : s;
    }

    @Transactional
    public void setImages(String productId, String color, List<String> urls) {
        jdbc.update("DELETE FROM product_images WHERE product_id = ? AND color = ?", productId, color);
        int pos = 0;
        for (String u : urls) {
            if (u == null || !URL_OK.matcher(u).matches()) continue;   // bỏ link không hợp lệ (vd javascript:)
            jdbc.update("INSERT INTO product_images(product_id, color, url, pos) VALUES (?, ?, ?, ?)", productId, color, u, pos++);
        }
    }
}
