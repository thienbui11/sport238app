CREATE TABLE products (
  id           VARCHAR(64) PRIMARY KEY,
  seq          BIGSERIAL,
  title        VARCHAR(500) NOT NULL,
  product_type VARCHAR(200) NOT NULL DEFAULT '',
  vendor       VARCHAR(200) NOT NULL DEFAULT '',
  active       BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE TABLE variants (
  id         VARCHAR(64) PRIMARY KEY,
  seq        BIGSERIAL,
  product_id VARCHAR(64) NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  sku        VARCHAR(64) NOT NULL,
  option1    VARCHAR(100) NOT NULL DEFAULT '',   -- size
  option2    VARCHAR(200) NOT NULL DEFAULT '',   -- màu / mẫu
  price      BIGINT NOT NULL DEFAULT 0,
  stock      INT NOT NULL DEFAULT 0
);
CREATE INDEX ix_variants_product ON variants(product_id);
-- Không khóa ngoại: ảnh được giữ nguyên khi nhập lại dữ liệu từ Sapo
CREATE TABLE product_images (
  id         BIGSERIAL PRIMARY KEY,
  product_id VARCHAR(64) NOT NULL,
  color      VARCHAR(200) NOT NULL DEFAULT '',
  url        VARCHAR(1000) NOT NULL,
  pos        INT NOT NULL DEFAULT 0
);
CREATE INDEX ix_images_product ON product_images(product_id);
CREATE TABLE settings (
  setting_key   VARCHAR(50) PRIMARY KEY,
  setting_value VARCHAR(200) NOT NULL
);
