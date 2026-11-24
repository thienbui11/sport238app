package com.sportshop.service;

import com.sportshop.config.ShopProperties;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowCallbackHandler;
import org.springframework.stereotype.Service;

/** Thông tin shop (tên, Messenger, Zalo): giá trị trong CSDL ghi đè giá trị mặc định ở cấu hình. */
@Service
public class ConfigService {
    private static final List<String> KEYS = List.of("shopName", "messengerUser", "zaloPhone");
    private final JdbcTemplate jdbc;
    private final ShopProperties props;

    public ConfigService(JdbcTemplate jdbc, ShopProperties props) { this.jdbc = jdbc; this.props = props; }

    public Map<String, String> get() {
        Map<String, String> c = new LinkedHashMap<>();
        c.put("shopName", props.shopName());
        c.put("messengerUser", props.messengerUser());
        c.put("zaloPhone", props.zaloPhone());
        jdbc.query("SELECT setting_key, setting_value FROM settings",
            (RowCallbackHandler) rs -> { if (c.containsKey(rs.getString(1))) c.put(rs.getString(1), rs.getString(2)); });
        return c;
    }

    public void set(Map<String, String> in) {
        for (String k : KEYS) {
            String v = in.get(k);
            if (v == null) continue;
            v = v.trim();
            if (v.length() > 100) v = v.substring(0, 100);
            jdbc.update("""
                INSERT INTO settings(setting_key, setting_value) VALUES (?, ?)
                ON CONFLICT (setting_key) DO UPDATE SET setting_value = EXCLUDED.setting_value""", k, v);
        }
    }
}
