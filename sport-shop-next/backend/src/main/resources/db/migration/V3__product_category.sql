-- Danh mục tự động (do bộ đọc Sapo gán mỗi lần nhập) và danh mục chọn tay trong trang quản trị (không bị ghi đè)
ALTER TABLE products ADD COLUMN category          VARCHAR(100) NOT NULL DEFAULT '';
ALTER TABLE products ADD COLUMN category_override VARCHAR(100) NOT NULL DEFAULT '';
