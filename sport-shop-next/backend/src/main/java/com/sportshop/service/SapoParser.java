package com.sportshop.service;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Chuyển các dòng của file Excel xuất từ Sapo POS thành sản phẩm web: phân loại 8 danh mục, tách size khỏi tên
 * rồi gộp các sản phẩm "mỗi size một sản phẩm" thành một sản phẩm nhiều size.
 * Java thuần (không phụ thuộc Spring hay POI) nên kiểm thử dễ. Logic giống hệt tools/sapo_xlsx_to_json.py.
 * Chỉ đọc giá bán lẻ và tồn kho. Giá nhập, giá vốn, giá buôn KHÔNG được đọc nên không thể lên web.
 */
public final class SapoParser {
    public static final String CUP = "Cờ, Cúp, Huy Chương", SHOE = "Giày bóng đá", CLUB = "Quần áo CLB/Đội tuyển", PLAIN = "Quần áo không logo",
            KIDS = "Quần áo trẻ em", ACC = "Phụ kiện thể thao", SOCK = "Vớ/tất ống đồng", BAD = "Cầu lông";
    public static final List<String> CATEGORIES = List.of(CUP, SHOE, CLUB, PLAIN, KIDS, ACC, SOCK, BAD);

    public record Variant(String id, String sku, String option1, String option2, long price, int stock) {}
    public record Product(String id, String title, String productType, String vendor, String category, List<Variant> variants) {}
    public record Result(List<Product> products, int totalProductsInFile, int droppedZeroPrice) {}

    private static final int F = Pattern.UNICODE_CHARACTER_CLASS;
    private static final Pattern STOCK_COL = Pattern.compile("^LC_.*Tồn kho ban đầu");
    private static final Pattern SIZE_PREFIX = Pattern.compile("^\\s*size\\s*", Pattern.CASE_INSENSITIVE | F);
    private static final Pattern SIZE_NAME = Pattern.compile("kích thước|kích cỡ|\\bcỡ\\b|\\bsize\\b|^số$", F);
    private static final Pattern SIZE_VAL = Pattern.compile("^(xxs|xs|s|m|l|xl|xxl|xxxl|xxxxl|[2-6]xl|free ?size|f|\\d{1,3}(?:[.,]5)?)$", Pattern.CASE_INSENSITIVE | F);

    private static final Set<String> WEB_TYPES = Set.of("Quần áo bóng đá", "Giày bóng đá", "Phụ kiện thể thao");
    private static final Pattern UNTYPED = Pattern.compile("^(giày|giầy|quần áo|quần cụt|áo cầu lông|vớ lexis|dây giày|áo bóng đá)", F);
    private static final Pattern TEAM = Pattern.compile("(?:^|[\\s\\-(])(?:mu|man u|manu|real|barca|bayern|liverpool|chelsea|arsenal|psg|inter|milan|tottenham|wolves|mc|tây ban nha|argentina|hà lan|brazil|bồ đào nha|pháp|đức|nhật|hàn quốc|mỹ|bỉ|vn|việt nam|croatia|uruguay|tuyển|bulls|anh)(?=$|[\\s\\-)\\d])", F);
    private static final Pattern CUP_RE = Pattern.compile("huy chương|cúp|(?:^|\\s)cờ(?:\\s|$)|kỷ niệm chương", F);
    private static final Pattern BAD_RE = Pattern.compile("cầu lông|vợt|bông cầu|shuttle", F);
    private static final Pattern SOCK_RE = Pattern.compile("ống đồng|(?:^|\\s)(?:vớ|tất)(?:\\s|$)", F);
    private static final Pattern KIDS_RE = Pattern.compile("trẻ em|kids|\\bqa trẻ", F);
    private static final Pattern SHOE_START = Pattern.compile("^(giày|giầy)", F);

    // Nhiều sản phẩm trong Sapo mỗi size là một sản phẩm riêng, size nằm trong tên ("Giày X - Size 42", "Quần áo Y- XL")
    private static final String NB = "(?<![A-Za-z0-9])";
    private static final Pattern SHOE_TAIL = Pattern.compile("^(?<base>.*?)[\\s\\-–]*" + NB + "(?:(?i:size)\\s*)?(?<size>3\\d|4\\d)\\s*$", Pattern.CASE_INSENSITIVE | F);
    private static final Pattern LETTER_TAIL = Pattern.compile("^(?<base>.*?)[\\s\\-–]*" + NB + "(?:(?i:size)\\s*)?(?<size>XXXXL|XXXL|XXL|XL|L|M|S)\\s*$", F);
    private static final Pattern LETTER_MID = Pattern.compile("^(?<a>.*?)\\s*[-–]\\s*(?<size>XXXXL|XXXL|XXL|XL|L|M|S)\\s*[-–]\\s*(?<b>.+)$", F);
    private static final List<String> LETTERS = List.of("XXS", "XS", "S", "M", "L", "XL", "XXL", "XXXL", "XXXXL");

    private static final Pattern WS = Pattern.compile("\\s+", F);
    private static final Pattern DASH = Pattern.compile("\\s*-\\s*", F);

    private SapoParser() {}

    /** Chuẩn hóa màu: bỏ khoảng trắng thừa quanh dấu gạch ngang ("Navy- tím nhạt" = "Navy-tím nhạt") */
    private static String nc(String v) {
        return DASH.matcher(WS.matcher(v).replaceAll(" ").trim()).replaceAll("-");
    }

    /** Các biến thể trùng cả size lẫn màu (Sapo không đặt tên phân biệt) được gắn nhãn theo giá để khách chọn được. */
    private static void labelDuplicates(List<Variant> variants) {
        Map<String, List<Integer>> groups = new java.util.LinkedHashMap<>();
        for (int i = 0; i < variants.size(); i++) groups.computeIfAbsent(variants.get(i).option1() + "\u0000" + variants.get(i).option2(), k -> new ArrayList<>()).add(i);
        for (List<Integer> idx : groups.values()) {
            if (idx.size() < 2) continue;
            String color = variants.get(idx.get(0)).option2();
            for (int i : idx) {
                Variant v = variants.get(i);
                String price = String.format(Locale.ROOT, "%,d", v.price()).replace(',', '.') + "đ";
                variants.set(i, new Variant(v.id(), v.sku(), v.option1(), color.equals("Mặc định") ? price : color + " (" + price + ")", v.price(), v.stock()));
            }
            Map<String, Integer> again = new HashMap<>();
            for (int i : idx) again.merge(variants.get(i).option1() + "\u0000" + variants.get(i).option2(), 1, Integer::sum);
            for (int i : idx) {
                Variant v = variants.get(i);
                if (again.get(v.option1() + "\u0000" + v.option2()) > 1)
                    variants.set(i, new Variant(v.id(), v.sku(), v.option1(), v.option2() + " [" + v.sku() + "]", v.price(), v.stock()));
            }
        }
    }

    private static final class Draft {
        String id, title, type, vendor, category;
        List<Variant> variants = new ArrayList<>();
    }

    private static final class Group {
        Map<String, String> head;
        List<Map<String, String>> rows = new ArrayList<>();
    }

    public static Result parse(List<Map<String, String>> rows) {
        List<Group> groups = new ArrayList<>();
        for (Map<String, String> r : rows) {
            if (!get(r, "Tên sản phẩm*").isEmpty()) { Group g = new Group(); g.head = r; groups.add(g); }
            if (!groups.isEmpty()) groups.get(groups.size() - 1).rows.add(r);
        }
        List<Draft> out = new ArrayList<>();
        Map<String, Draft> byKey = new HashMap<>();
        Set<String> used = new HashSet<>();
        int dropped = 0;

        for (Group g : groups) {
            String title = get(g.head, "Tên sản phẩm*"), ptype = get(g.head, "Loại sản phẩm");
            String[] attr = new String[3];
            for (int i = 0; i < 3; i++) attr[i] = get(g.head, "Thuộc tính " + (i + 1)).toLowerCase(Locale.ROOT);
            String[][] vals = new String[3][g.rows.size()];
            for (int i = 0; i < 3; i++) for (int k = 0; k < g.rows.size(); k++) vals[i][k] = normalize(get(g.rows.get(k), "Giá trị thuộc tính " + (i + 1)));

            // Vai trò từng thuộc tính: màu / size (theo tên hoặc theo giá trị) / khác
            String[] role = new String[3];
            boolean hasSize = false;
            for (int i = 0; i < 3; i++) {
                boolean any = false, allSize = true;
                for (String v : vals[i]) if (!v.isEmpty()) { any = true; if (!SIZE_VAL.matcher(v).matches()) allSize = false; }
                if (attr[i].contains("màu")) role[i] = "color";
                else if (!hasSize && (SIZE_NAME.matcher(attr[i]).find() || (any && allSize))) { role[i] = "size"; hasSize = true; }
                else role[i] = "other";
            }

            List<Variant> variants = new ArrayList<>();
            for (int k = 0; k < g.rows.size(); k++) {
                Map<String, String> r = g.rows.get(k);
                String size = "", color = "";
                List<String> other = new ArrayList<>();
                for (int i = 0; i < 3; i++) {
                    String v = vals[i][k];
                    if (v.isEmpty()) continue;
                    if (role[i].equals("size")) size = v; else if (role[i].equals("color")) color = nc(v); else other.add(nc(v));
                }
                long price = Math.round(num(get(r, "PL_Giá bán lẻ")));
                if (price <= 0) { dropped++; continue; }
                String sku = get(r, "Mã SKU*"), vid = sku;
                int n = 2;
                while (used.contains(vid)) vid = sku + "-" + n++;   // SKU trùng thì thêm hậu tố để không mất phiên bản
                used.add(vid);
                List<String> o2 = new ArrayList<>();
                if (!color.isEmpty()) o2.add(color);
                o2.addAll(other);
                double stock = 0;
                for (Map.Entry<String, String> e : r.entrySet()) if (STOCK_COL.matcher(e.getKey()).find()) stock += num(e.getValue());
                variants.add(new Variant(vid, sku, size, o2.isEmpty() ? "Mặc định" : String.join(" / ", o2), price, (int) Math.max(0, Math.round(stock))));
            }
            if (variants.isEmpty()) continue;
            labelDuplicates(variants);

            List<String> sizes = new ArrayList<>();
            for (Variant v : variants) sizes.add(v.option1());
            String cat = classify(title, ptype, sizes);
            if (cat == null) continue;

            boolean merged = false;
            if (variants.size() == 1 && variants.get(0).option1().isEmpty() && (cat.equals(SHOE) || cat.equals(CLUB) || cat.equals(PLAIN) || cat.equals(KIDS) || cat.equals(BAD))) {
                String[] sp = splitSize(title);
                if (sp != null && (isDigits(sp[1]) == cat.equals(SHOE))) {      // giày dùng size số, quần áo dùng size chữ
                    title = sp[0];
                    Variant v = variants.get(0);
                    variants.set(0, new Variant(v.id(), v.sku(), sp[1], v.option2(), v.price(), v.stock()));
                    String c2 = classify(title, ptype, List.of(sp[1]));
                    if (c2 != null) cat = c2;
                    merged = true;
                }
            }
            Draft d = new Draft();
            d.title = title; d.type = ptype; d.vendor = get(g.head, "Nhãn hiệu"); d.category = cat; d.variants = variants;
            String key = merged ? cat + "\u0000" + mergeKey(title) : null;
            if (key != null && byKey.containsKey(key)) {      // cùng sản phẩm, khác size: gộp vào sản phẩm đã có
                Draft t = byKey.get(key);
                t.variants.addAll(variants);
                if (t.vendor.isEmpty()) t.vendor = d.vendor;
            } else {
                out.add(d);
                if (key != null) byKey.put(key, d);
            }
        }

        List<Product> products = new ArrayList<>();
        for (Draft d : out) {
            d.variants.sort(Comparator.comparingInt(v -> sizeKey(v.option1())));   // sắp size, ổn định
            products.add(new Product(d.variants.get(0).id(), d.title, d.type, d.vendor, d.category, List.copyOf(d.variants)));
        }
        return new Result(products, groups.size(), dropped);
    }

    /** Trả về tên danh mục, hoặc null nếu sản phẩm không đưa lên web (shop còn bán đồ mẹ và bé). */
    public static String classify(String name, String ptype, List<String> sizes) {
        ptype = ptype == null ? "" : ptype.trim();
        String n = name.toLowerCase(Locale.ROOT).trim().replaceAll("[\\s\\u00A0]+", " ");
        if (!WEB_TYPES.contains(ptype) && !(ptype.isEmpty() && UNTYPED.matcher(n).find())) return null;
        if (CUP_RE.matcher(n).find()) return CUP;
        if (BAD_RE.matcher(n).find()) return BAD;
        if (SOCK_RE.matcher(n).find()) return SOCK;
        if (ptype.equals("Phụ kiện thể thao") || n.startsWith("dây giày")) return ACC;
        if (SHOE_START.matcher(n).find()) return SHOE;
        boolean anySize = false, allDigits = true;
        for (String s : sizes) if (!s.isEmpty()) { anySize = true; if (!isDigits(s)) allDigits = false; }
        if (KIDS_RE.matcher(n).find() || (anySize && allDigits)) return KIDS;
        if (TEAM.matcher(n).find()) return CLUB;
        return PLAIN;
    }

    /** Trả về {tên gốc, size} nếu tên có chứa size, ngược lại null. */
    static String[] splitSize(String title) {
        Matcher m = LETTER_MID.matcher(title);
        if (m.matches()) return new String[]{(m.group("a") + " - " + m.group("b")).trim(), m.group("size")};
        for (Pattern rx : List.of(SHOE_TAIL, LETTER_TAIL)) {
            m = rx.matcher(title);
            if (m.matches() && !m.group("base").trim().isEmpty()) return new String[]{strip(m.group("base").trim(), " -–"), m.group("size").toUpperCase(Locale.ROOT)};
        }
        return null;
    }

    private static String strip(String s, String chars) {
        int a = 0, b = s.length();
        while (a < b && chars.indexOf(s.charAt(a)) >= 0) a++;
        while (b > a && chars.indexOf(s.charAt(b - 1)) >= 0) b--;
        return s.substring(a, b);
    }

    private static String mergeKey(String title) {
        String t = title.toLowerCase(Locale.ROOT).trim().replaceAll("[\\s\\u00A0]+", " ").replaceAll("\\s*[-–]\\s*", "-");
        return strip(t, "-");
    }

    private static int sizeKey(String s) {
        if (s.isEmpty()) return 200_000;
        if (isDigits(s)) return Integer.parseInt(s);
        int i = LETTERS.indexOf(s);
        return 100_000 + (i >= 0 ? i : 99);
    }

    private static boolean isDigits(String s) {
        if (s.isEmpty()) return false;
        for (int i = 0; i < s.length(); i++) if (!Character.isDigit(s.charAt(i))) return false;
        return true;
    }

    private static String get(Map<String, String> r, String k) {
        String v = r.get(k);
        return v == null ? "" : v.trim();
    }

    /** "Size 1" -> "1"; "Mặc định" -> "" (không có size) */
    private static String normalize(String v) {
        v = SIZE_PREFIX.matcher(v).replaceFirst("").trim();
        return v.equalsIgnoreCase("mặc định") ? "" : v;
    }

    private static double num(String s) {
        try { return Double.parseDouble(s.replace(",", "")); } catch (Exception e) { return 0; }
    }
}
