package com.sportshop.service;

import java.io.IOException;
import java.io.InputStream;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.apache.poi.ss.usermodel.Cell;
import org.apache.poi.ss.usermodel.DataFormatter;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.ss.usermodel.Sheet;
import org.apache.poi.ss.usermodel.Workbook;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.springframework.stereotype.Service;

/** Đọc sheet đầu tiên của file .xlsx thành danh sách dòng: tên cột -> giá trị chữ. */
@Service
public class ExcelImportService {
    private final DataFormatter formatter = new DataFormatter();

    public List<Map<String, String>> read(InputStream in) throws IOException {
        try (Workbook wb = new XSSFWorkbook(in)) {
            Sheet sheet = wb.getSheetAt(0);
            Row head = sheet.getRow(0);
            if (head == null) return List.of();
            int n = head.getLastCellNum();
            String[] names = new String[n];
            for (int i = 0; i < n; i++) names[i] = text(head.getCell(i)).trim();

            List<Map<String, String>> rows = new ArrayList<>();
            for (int r = 1; r <= sheet.getLastRowNum(); r++) {
                Row row = sheet.getRow(r);
                if (row == null) continue;
                Map<String, String> m = new LinkedHashMap<>();
                for (int i = 0; i < n; i++) if (!names[i].isEmpty()) m.put(names[i], text(row.getCell(i)));
                rows.add(m);
            }
            return rows;
        }
    }

    private String text(Cell c) {
        if (c == null) return "";
        return switch (c.getCellType()) {
            case STRING -> c.getStringCellValue().trim();
            case NUMERIC -> BigDecimal.valueOf(c.getNumericCellValue()).stripTrailingZeros().toPlainString();
            case BOOLEAN -> String.valueOf(c.getBooleanCellValue());
            case FORMULA -> formatter.formatCellValue(c).trim();
            default -> "";
        };
    }
}
