package com.sportshop.service;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.FileInputStream;
import java.io.InputStream;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.condition.EnabledIfEnvironmentVariable;

/**
 * Đối chiếu bộ đọc Java với bộ đọc Python trên CÙNG một file Excel Sapo thật.
 * Chạy:  py sport-shop-app/tools/sapo_xlsx_to_json.py file.xlsx py.json
 *        SAPO_XLSX=file.xlsx PY_JSON=py.json mvn -B test -Dtest=ParityWithPythonTest
 * Không đặt hai biến môi trường thì bài này được bỏ qua.
 */
@EnabledIfEnvironmentVariable(named = "SAPO_XLSX", matches = ".+")
class ParityWithPythonTest {
    @Test
    void javaGivesExactlyTheSameProductsAsPython() throws Exception {
        List<String> java = new ArrayList<>();
        SapoParser.Result r;
        try (InputStream in = new FileInputStream(System.getenv("SAPO_XLSX"))) {
            r = SapoParser.parse(new ExcelImportService().read(in));
        }
        for (SapoParser.Product p : r.products()) java.add(line(p.id(), p.title(), p.productType(), p.vendor(), p.category(), variants(p)));

        List<String> py = new ArrayList<>();
        JsonNode root = new ObjectMapper().readTree(Path.of(System.getenv("PY_JSON")).toFile());
        for (JsonNode p : root.get("products")) {
            StringBuilder v = new StringBuilder();
            for (JsonNode x : p.get("variants"))
                v.append(String.join("|", x.get("id").asText(), x.get("sku").asText(), x.get("option1").asText(), x.get("option2").asText(),
                        String.valueOf(x.get("price").asLong()), String.valueOf(x.get("inventory_quantity").asInt()))).append(";");
            py.add(line(p.get("id").asText(), p.get("title").asText(), p.get("product_type").asText(), p.get("vendor").asText(), p.get("category").asText(), v.toString()));
        }
        assertEquals(py.size(), java.size(), "số sản phẩm");
        for (int i = 0; i < py.size(); i++) assertEquals(py.get(i), java.get(i), "sản phẩm thứ " + (i + 1));
        System.out.printf("Python = Java: %d sản phẩm, %d phiên bản, %d sản phẩm trong file, bỏ %d phiên bản giá 0%n",
                r.products().size(), r.products().stream().mapToInt(p -> p.variants().size()).sum(), r.totalProductsInFile(), r.droppedZeroPrice());
    }

    private static String variants(SapoParser.Product p) {
        StringBuilder v = new StringBuilder();
        for (SapoParser.Variant x : p.variants())
            v.append(String.join("|", x.id(), x.sku(), x.option1(), x.option2(), String.valueOf(x.price()), String.valueOf(Math.max(0, x.stock())))).append(";");
        return v.toString();
    }

    private static String line(String... parts) { return String.join(" ‖ ", parts); }
}
