"use strict";
// Tầng dữ liệu: SQLite có sẵn trong Node (không cần cài thêm gì). Muốn đổi sang MySQL/Postgres sau này chỉ cần sửa file này.
const { DatabaseSync } = require("node:sqlite");
const fs = require("fs"), path = require("path");

const DATA = process.env.DATA_DIR || path.join(__dirname, "..", "data");
fs.mkdirSync(path.join(DATA, "uploads"), { recursive: true });
const db = new DatabaseSync(path.join(DATA, "shop.db"));
db.exec(`
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS products(id TEXT PRIMARY KEY, title TEXT NOT NULL, product_type TEXT DEFAULT '', vendor TEXT DEFAULT '', active INTEGER DEFAULT 1);
CREATE TABLE IF NOT EXISTS variants(id TEXT PRIMARY KEY, product_id TEXT NOT NULL, sku TEXT, option1 TEXT DEFAULT '', option2 TEXT DEFAULT '', price INTEGER DEFAULT 0, stock INTEGER DEFAULT 0);
CREATE INDEX IF NOT EXISTS ix_variants_product ON variants(product_id);
CREATE TABLE IF NOT EXISTS images(id INTEGER PRIMARY KEY AUTOINCREMENT, product_id TEXT NOT NULL, color TEXT DEFAULT '', url TEXT NOT NULL, pos INTEGER DEFAULT 0);
CREATE INDEX IF NOT EXISTS ix_images_product ON images(product_id);
CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);
`);

// Thêm cột mới cho CSDL cũ (tên hiển thị, mô tả, ẩn, nổi bật): không đụng tới dữ liệu có sẵn
const have = db.prepare("PRAGMA table_info(products)").all().map((c) => c.name);
for (const [c, d] of [["display_title", "TEXT DEFAULT ''"], ["description", "TEXT DEFAULT ''"], ["hidden", "INTEGER DEFAULT 0"], ["featured", "INTEGER DEFAULT 0"], ["category", "TEXT DEFAULT ''"], ["category_override", "TEXT DEFAULT ''"]])
  if (!have.includes(c)) db.exec(`ALTER TABLE products ADD COLUMN ${c} ${d}`);

const tx = (fn) => { db.exec("BEGIN"); try { const r = fn(); db.exec("COMMIT"); return r; } catch (e) { db.exec("ROLLBACK"); throw e; } };

// Danh mục sản phẩm; all=true dùng cho admin (kể cả sản phẩm đang ẩn)
function catalog(all) {
  const ps = db.prepare(`SELECT id,title,display_title,description,product_type,vendor,category,category_override,active,hidden,featured FROM products ${all ? "" : "WHERE active=1 AND hidden=0"} ORDER BY rowid`).all();
  const by = {};
  for (const v of db.prepare("SELECT * FROM variants").all())
    (by[v.product_id] = by[v.product_id] || []).push({ id: v.id, sku: v.sku, option1: v.option1, option2: v.option2, price: v.price, inventory_quantity: v.stock });
  const products = ps.map((p) => ({ ...p, category_auto: p.category || "", category: p.category_override || p.category || "Phụ kiện thể thao", category_override: p.category_override || "", display_title: p.display_title || "", description: p.description || "", hidden: !!p.hidden, featured: !!p.featured, variants: by[p.id] || [] })).filter((p) => p.variants.length);
  const images = {};  // khóa: "idSP" (chung) hoặc "idSP:Màu" (riêng theo màu)
  for (const i of db.prepare("SELECT product_id,color,url FROM images ORDER BY pos,id").all())
    (images[i.color ? `${i.product_id}:${i.color}` : i.product_id] ||= []).push(i.url);
  return { products, images };
}

// Nhập danh sách từ Sapo. Giữ nguyên ảnh; sản phẩm không còn trong file sẽ bị ẩn (không xóa).
function importProducts(list) {
  if (!Array.isArray(list) || list.length === 0) throw new Error("bad_format"); // chặn file rỗng để không lỡ ẩn toàn bộ sản phẩm
  let nv = 0;
  tx(() => {
    db.exec("UPDATE products SET active=0");
    const up = db.prepare("INSERT INTO products(id,title,product_type,vendor,category,active) VALUES(?,?,?,?,?,1) ON CONFLICT(id) DO UPDATE SET title=excluded.title,product_type=excluded.product_type,vendor=excluded.vendor,category=excluded.category,active=1");
    const del = db.prepare("DELETE FROM variants WHERE product_id=?");
    const ins = db.prepare("INSERT OR REPLACE INTO variants(id,product_id,sku,option1,option2,price,stock) VALUES(?,?,?,?,?,?,?)");
    for (const p of list) {
      if (!p.id || !p.title || !Array.isArray(p.variants)) throw new Error("bad_product");
      up.run(String(p.id), String(p.title), String(p.product_type || ""), String(p.vendor || ""), String(p.category || ""));
      del.run(String(p.id));
      for (const v of p.variants) {
        ins.run(String(v.id), String(p.id), String(v.sku || v.id), String(v.option1 || ""), String(v.option2 || "Mặc định"), Math.round(Number(v.price) || 0), Math.round(Number(v.inventory_quantity) || 0));
        nv++;
      }
    }
  });
  return { products: list.length, variants: nv };
}

const CATEGORIES = ["Cờ, Cúp, Huy Chương", "Giày bóng đá", "Quần áo CLB/Đội tuyển", "Quần áo không logo", "Quần áo trẻ em", "Phụ kiện thể thao", "Vớ/tất ống đồng", "Cầu lông"];

// Thông tin chỉ có trên web (Sapo không quản lý): không bị ghi đè khi nhập lại từ Sapo
function setProductInfo(id, o) {
  const clip = (s, n) => String(s || "").trim().slice(0, n);
  const cat = CATEGORIES.includes(o.category) ? o.category : "";   // để trống = tự động theo tên
  return db.prepare("UPDATE products SET display_title=?, description=?, hidden=?, featured=?, category_override=? WHERE id=?")
    .run(clip(o.display_title, 200), clip(o.description, 4000), o.hidden ? 1 : 0, o.featured ? 1 : 0, cat, String(id)).changes > 0;
}

function setImages(productId, color, urls) {
  const ok = urls.filter((u) => typeof u === "string" && /^(\/uploads\/[\w.-]+|https?:\/\/\S+)$/.test(u));
  tx(() => {
    db.prepare("DELETE FROM images WHERE product_id=? AND color=?").run(String(productId), color);
    const ins = db.prepare("INSERT INTO images(product_id,color,url,pos) VALUES(?,?,?,?)");
    ok.forEach((u, i) => ins.run(String(productId), color, u, i));
  });
}

const DEFAULTS = () => ({ shopName: process.env.SHOP_NAME || "SPORT 238", messengerUser: process.env.MESSENGER_USER || "Sport238", zaloPhone: process.env.ZALO_PHONE || "0962374770" });
function getConfig() {
  const c = DEFAULTS();
  for (const r of db.prepare("SELECT key,value FROM settings").all()) if (r.key in c) c[r.key] = r.value;
  return c;
}
function setConfig(o) {
  const up = db.prepare("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value");
  for (const k of Object.keys(DEFAULTS())) if (typeof o[k] === "string") up.run(k, o[k].trim().slice(0, 100));
}

function seedIfEmpty() {
  const f = path.join(DATA, "seed-products.json");
  if (db.prepare("SELECT COUNT(*) n FROM products").get().n === 0 && fs.existsSync(f)) {
    const r = importProducts(JSON.parse(fs.readFileSync(f, "utf8")).products);
    console.log(`Đã nạp dữ liệu mẫu: ${r.products} sản phẩm, ${r.variants} phiên bản`);
  }
}

module.exports = { DATA, catalog, importProducts, setImages, setProductInfo, getConfig, setConfig, seedIfEmpty };
