-- Thông tin chỉ có trên web (Sapo không quản lý), không bị ghi đè khi nhập lại từ Sapo
ALTER TABLE products ADD COLUMN display_title VARCHAR(500) NOT NULL DEFAULT '';
ALTER TABLE products ADD COLUMN description   TEXT         NOT NULL DEFAULT '';
ALTER TABLE products ADD COLUMN hidden        BOOLEAN      NOT NULL DEFAULT FALSE;
ALTER TABLE products ADD COLUMN featured      BOOLEAN      NOT NULL DEFAULT FALSE;
