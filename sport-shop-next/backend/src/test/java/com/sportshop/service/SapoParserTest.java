package com.sportshop.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.Test;

class SapoParserTest {
    private static Map<String, String> row(String... kv) {
        var m = new HashMap<String, String>();
        for (int i = 0; i < kv.length; i += 2) m.put(kv[i], kv[i + 1]);
        return m;
    }

    @Test
    void groupsVariantsAndClassifies() {
        var rows = List.of(
            row("Tên sản phẩm*", "Quần áo AMAC- Blur", "Loại sản phẩm", "Quần áo bóng đá", "Thuộc tính 1", "Kích thước", "Thuộc tính 2", "Màu sắc",
                "Giá trị thuộc tính 1", "Size S", "Giá trị thuộc tính 2", "Trắng", "Mã SKU*", "PVN1", "PL_Giá bán lẻ", "150000", "LC_CN1_Tồn kho ban đầu*", "0"),
            row("Giá trị thuộc tính 1", "M", "Giá trị thuộc tính 2", "Trắng", "Mã SKU*", "PVN2", "PL_Giá bán lẻ", "150000", "LC_CN1_Tồn kho ban đầu*", "2"),
            row("Giá trị thuộc tính 1", "L", "Giá trị thuộc tính 2", "Trắng", "Mã SKU*", "PVN3", "PL_Giá bán lẻ", "0", "LC_CN1_Tồn kho ban đầu*", "5"),
            row("Tên sản phẩm*", "Bình sữa", "Loại sản phẩm", "Đồ cho bé", "Mã SKU*", "PVN9", "PL_Giá bán lẻ", "50000"));
        var r = SapoParser.parse(rows);
        assertEquals(1, r.products().size());
        assertEquals(2, r.totalProductsInFile());
        assertEquals(1, r.droppedZeroPrice());
        var p = r.products().get(0);
        assertEquals(SapoParser.PLAIN, p.category());
        assertEquals(List.of("S", "M"), p.variants().stream().map(SapoParser.Variant::option1).toList());
        assertEquals(0, p.variants().get(0).stock());
    }

    @Test
    void mergesProductsThatAreSplitBySize() {
        List<Map<String, String>> rows = new ArrayList<>();
        for (String s : List.of("43", "40", "41"))
            rows.add(row("Tên sản phẩm*", "Giày Promax PR-21 - Xanh - Size " + s, "Loại sản phẩm", "Giày bóng đá", "Mã SKU*", "G" + s,
                "PL_Giá bán lẻ", "300000", "LC_CN1_Tồn kho ban đầu*", s.equals("40") ? "0" : "1"));
        var r = SapoParser.parse(rows);
        assertEquals(1, r.products().size());
        var p = r.products().get(0);
        assertEquals("Giày Promax PR-21 - Xanh", p.title());
        assertEquals(SapoParser.SHOE, p.category());
        assertEquals(List.of("40", "41", "43"), p.variants().stream().map(SapoParser.Variant::option1).toList());
    }

    @Test
    void classifiesAllCategories() {
        assertEquals(SapoParser.CUP, SapoParser.classify("Cúp iWin G1507", "Phụ kiện thể thao", List.of()));
        assertEquals(SapoParser.SOCK, SapoParser.classify("Tất Dệt Kim IZI", "Phụ kiện thể thao", List.of()));
        assertEquals(SapoParser.BAD, SapoParser.classify("Áo cầu lông vicky - Size M", "", List.of("M")));
        assertEquals(SapoParser.KIDS, SapoParser.classify("Quần áo Strivend", "Quần áo bóng đá", List.of("1", "3", "5")));
        assertEquals(SapoParser.CLUB, SapoParser.classify("Quần áo HD 2026- MU - Mẫu Mới", "Quần áo bóng đá", List.of("S", "M")));
        assertNull(SapoParser.classify("Bình sữa", "Đồ cho bé", List.of()));
    }
}
