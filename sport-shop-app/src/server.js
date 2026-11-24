"use strict";
// Máy chủ HTTP: API + phục vụ giao diện. Thêm chức năng mới = thêm một khối `if` trong api() (hoặc tách file route riêng).
const http = require("http"), fs = require("fs"), path = require("path"), crypto = require("crypto");
const db = require("./db");

const PORT = +process.env.PORT || 3000;
const PUB = path.join(__dirname, "..", "public");
const PASS = process.env.ADMIN_PASSWORD || "admin123";
if (!process.env.ADMIN_PASSWORD) console.warn("⚠ Chưa đặt ADMIN_PASSWORD, đang dùng mật khẩu mặc định 'admin123'. Hãy đổi trước khi đưa lên mạng!");

const sessions = new Map(), fails = new Map();
const MIME = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".json": "application/json", ".jpg": "image/jpeg", ".png": "image/png", ".webp": "image/webp", ".gif": "image/gif", ".ico": "image/x-icon" };
const sha = (s) => crypto.createHash("sha256").update(String(s)).digest();

function send(res, code, body, type, headers) {
  res.writeHead(code, { "Content-Type": type || "application/json; charset=utf-8", "X-Content-Type-Options": "nosniff", ...headers });
  res.end(body);
}
const json = (res, code, obj, h) => send(res, code, JSON.stringify(obj), null, h);
function readBody(req, max = 2e6) {
  return new Promise((ok, no) => {
    const c = []; let n = 0;
    req.on("data", (d) => { n += d.length; if (n > max) { no(new Error("too_large")); req.destroy(); } else c.push(d); });
    req.on("end", () => ok(Buffer.concat(c)));
    req.on("error", no);
  });
}
const readJson = async (req, max) => { const b = await readBody(req, max); return b.length ? JSON.parse(b) : {}; };
const sidOf = (req) => { const m = (req.headers.cookie || "").match(/(?:^|;\s*)sid=([a-f0-9]+)/); return m ? m[1] : ""; };
const isAdmin = (req) => { const sid = sidOf(req); return !!sid && (sessions.get(sid) || 0) > Date.now(); };
const pruneSessions = () => { const now = Date.now(); for (const [k, t] of sessions) if (t <= now) sessions.delete(k); };
function sniff(b) { // nhận dạng ảnh theo nội dung, không tin tên file
  if (b[0] === 0xff && b[1] === 0xd8 && b[2] === 0xff) return "jpg";
  if (b.slice(0, 4).equals(Buffer.from([0x89, 0x50, 0x4e, 0x47]))) return "png";
  if (b.slice(0, 4).toString() === "GIF8") return "gif";
  if (b.slice(0, 4).toString() === "RIFF" && b.slice(8, 12).toString() === "WEBP") return "webp";
  return null;
}
function file(res, f, cache) {
  fs.stat(f, (e, st) => {
    if (e || !st.isFile()) return json(res, 404, { error: "not_found" });
    res.writeHead(200, { "Content-Type": MIME[path.extname(f).toLowerCase()] || "application/octet-stream", "Cache-Control": cache || "no-cache", "X-Content-Type-Options": "nosniff" });
    fs.createReadStream(f).pipe(res);
  });
}

async function api(req, res, u, p, m) {
  // ----- công khai -----
  if (m === "GET" && p === "/api/products") return json(res, 200, db.catalog(false), { "Cache-Control": "public, max-age=30" });
  if (m === "GET" && p === "/api/config") return json(res, 200, db.getConfig());
  if (m === "POST" && p === "/api/admin/login") {
    const ip = req.socket.remoteAddress, f = fails.get(ip) || { n: 0, t: Date.now() };
    if (Date.now() - f.t > 6e5) { f.n = 0; f.t = Date.now(); }
    if (f.n >= 5) return json(res, 429, { error: "too_many_attempts" });
    const { password } = await readJson(req, 1e4);
    if (!crypto.timingSafeEqual(sha(password), sha(PASS))) { f.n++; fails.set(ip, f); return json(res, 401, { error: "wrong_password" }); }
    pruneSessions();
    const sid = crypto.randomBytes(24).toString("hex");
    sessions.set(sid, Date.now() + 12 * 36e5);
    return json(res, 200, { ok: true }, { "Set-Cookie": `sid=${sid}; HttpOnly; SameSite=Lax; Path=/; Max-Age=43200` });
  }
  if (m === "POST" && p === "/api/admin/logout") {   // cookie HttpOnly nên phải xóa ở máy chủ (JavaScript không xóa được)
    sessions.delete(sidOf(req));
    return json(res, 200, { ok: true }, { "Set-Cookie": "sid=; HttpOnly; SameSite=Lax; Path=/; Max-Age=0" });
  }
  // ----- quản trị (cần đăng nhập) -----
  if (!p.startsWith("/api/admin/")) return json(res, 404, { error: "not_found" });
  if (!isAdmin(req)) return json(res, 401, { error: "unauthorized" });
  if (m === "GET" && p === "/api/admin/products") return json(res, 200, db.catalog(true));
  if (m === "POST" && p === "/api/admin/import") {
    // Bản Node chỉ nhận JSON; tệp Excel (gửi dạng multipart) thì báo rõ để trang quản trị hướng dẫn
    if (/multipart\/form-data/i.test(req.headers["content-type"] || "")) { req.resume(); return json(res, 415, { error: "xlsx_not_supported" }); }
    return json(res, 200, db.importProducts((await readJson(req, 3e7)).products));
  }
  const mp = p.match(/^\/api\/admin\/products\/([^/]+)$/);
  if (m === "PUT" && mp) return db.setProductInfo(mp[1], await readJson(req, 5e4)) ? json(res, 200, { ok: true }) : json(res, 404, { error: "not_found" });
  if (m === "POST" && p === "/api/admin/images") { const d = await readJson(req, 1e5); db.setImages(d.product_id, d.color || "", d.urls || []); return json(res, 200, { ok: true }); }
  if (m === "POST" && p === "/api/admin/config") { db.setConfig(await readJson(req, 1e4)); return json(res, 200, { ok: true }); }
  if (m === "POST" && p === "/api/admin/upload") {
    const buf = await readBody(req, 8e6), ext = sniff(buf);
    if (!ext) return json(res, 400, { error: "not_an_image" });
    const name = crypto.randomBytes(10).toString("hex") + "." + ext;
    fs.writeFileSync(path.join(db.DATA, "uploads", name), buf);
    return json(res, 200, { url: "/uploads/" + name });
  }
  return json(res, 404, { error: "not_found" });
}

http.createServer(async (req, res) => {
  try {
    const u = new URL(req.url, "http://x"), p = decodeURIComponent(u.pathname);
    if (p.startsWith("/api/")) return await api(req, res, u, p, req.method);
    if (req.method !== "GET") return json(res, 405, { error: "method_not_allowed" });
    if (p.startsWith("/uploads/")) return file(res, path.join(db.DATA, "uploads", path.basename(p)), "public, max-age=86400");
    if (p === "/admin") return file(res, path.join(PUB, "admin.html"));
    const f = path.join(PUB, p === "/" ? "index.html" : p);
    if (!f.startsWith(PUB + path.sep)) return json(res, 403, { error: "forbidden" });
    return file(res, f);
  } catch (e) {
    const big = e.message === "too_large", bad = e instanceof SyntaxError || e instanceof URIError || e.message === "bad_format" || e.message === "bad_product";
    if (!big && !bad) console.error(e);
    json(res, big ? 413 : bad ? 400 : 500, { error: big ? "too_large" : bad ? "bad_request" : "server_error" });
  }
}).listen(PORT, () => { db.seedIfEmpty(); console.log(`Web chạy tại http://localhost:${PORT}  |  Quản trị: http://localhost:${PORT}/admin`); });
