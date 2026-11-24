# SPORT 238 – web bán đồ thể thao

Danh sách sản phẩm, trang chi tiết (ảnh, size, màu, tồn kho), giỏ hàng, chốt đơn qua Zalo/Messenger, trang quản trị.
Không có thanh toán online. Dữ liệu hàng hóa lấy từ file Excel xuất từ Sapo POS.

> **Đưa lên mạng bán thật và cập nhật hằng ngày:** xem `HUONG-DAN-DUA-LEN-MANG.md`.

## Chạy thử
Cần **Node.js 22.9 trở lên** (không cần `npm install`, vì không dùng thư viện ngoài).

    cp .env.example .env      # rồi sửa mật khẩu admin, tên Facebook, số Zalo
    npm start

- Web bán hàng: http://localhost:3000
- Quản trị:     http://localhost:3000/admin

Lần chạy đầu, hệ thống tự nạp 175 sản phẩm mẫu từ `data/seed-products.json`.

## Công việc hằng ngày
1. **Cập nhật hàng:** xuất Excel từ Sapo, chạy `python tools/sapo_xlsx_to_json.py file.xlsx san-pham.json` (cần `pip install pandas openpyxl`), rồi vào /admin, tab *Nhập từ Sapo*. Ảnh đã thêm được giữ nguyên.
2. **Thêm ảnh:** /admin, tab *Sản phẩm & ảnh*, bấm vào sản phẩm, tải ảnh lên hoặc dán link, bấm Lưu ảnh. Sản phẩm nhiều màu có ảnh riêng cho từng màu.
3. **Danh mục:** web tự xếp sản phẩm vào 8 danh mục theo tên và loại (xem hàm `classify` trong `tools/sapo_xlsx_to_json.py` và `SapoParser.java` của bản Spring Boot). Muốn chuyển một sản phẩm sang danh mục khác, chọn tay trong /admin (không bị ghi đè khi nhập lại từ Sapo). Sản phẩm không phải đồ thể thao (đồ mẹ và bé) tự bị loại.
- **Gộp size:** nhiều sản phẩm trong Sapo mỗi size là một sản phẩm riêng (tên có "Size 42", "- XL"). Công cụ tách size khỏi tên và gộp thành một sản phẩm nhiều size để khách chọn size ở trang chi tiết.

## Nạp ảnh hàng loạt
Đặt tên ảnh theo **mã SKU** trong Sapo: `PVN3939.jpg` là ảnh chính, `PVN3939-1.jpg`, `PVN3939-2.jpg`… là ảnh phụ. Mã SKU là mã của từng phiên bản nên ảnh tự gắn đúng **màu**.
Bật trang quản trị, rồi **kéo thả thư mục ảnh vào tệp `nap-anh.bat`** (hoặc `python tools/nap_anh.py "D:/anh-san-pham"`; thêm `--dry-run` để xem trước). Ảnh được xoay đúng chiều, thu nhỏ, đổi WebP; ảnh cũ được giữ; chạy lại không nạp trùng. Báo cáo HTML (thư mục `bao-cao/`) liệt kê tệp sai tên và **sản phẩm còn thiếu ảnh kèm mã SKU** để chụp tiếp. Xong thì bấm `cap-nhat-web.bat` để ảnh lên web.

## Cấu trúc
    src/server.js       máy chủ HTTP, API, đăng nhập admin, tải ảnh lên
    src/db.js           toàn bộ truy vấn SQLite (muốn đổi cơ sở dữ liệu thì chỉ sửa file này)
    public/index.html   giao diện bán hàng (gọi /api/products, /api/config)
    public/admin.html   giao diện quản trị (gọi /api/admin/*)
    data/               shop.db (tự tạo), uploads/ (ảnh), seed-products.json
    tools/              chuyển Excel Sapo thành JSON

## API
| Đường dẫn | Mô tả |
|---|---|
| GET /api/products | sản phẩm đang bán + ảnh |
| GET /api/config | tên shop, Messenger, Zalo |
| POST /api/admin/login | đăng nhập (sai quá 5 lần thì khóa 10 phút) |
| GET /api/admin/products | toàn bộ sản phẩm kể cả đang ẩn |
| POST /api/admin/import | nhập file JSON từ Sapo |
| POST /api/admin/images | đặt danh sách ảnh cho một sản phẩm / màu |
| POST /api/admin/upload | tải ảnh lên (JPG, PNG, WEBP, GIF, tối đa 8MB) |
| POST /api/admin/config | lưu thông tin shop |

## Thêm chức năng sau này
- **API mới:** thêm một khối `if (m === "GET" && p === "/api/...")` trong hàm `api()` của `src/server.js`; câu truy vấn đặt trong `src/db.js`.
- **Bảng mới** (đơn hàng, khách, mã giảm giá...): thêm `CREATE TABLE IF NOT EXISTS` trong `src/db.js`.
- **Nên làm tiếp:** lưu đơn tạo từ giỏ hàng để theo dõi trong admin, ẩn/hiện sản phẩm thủ công, sản phẩm nổi bật, mô tả sản phẩm, trang bảng size.

## Trước khi đưa lên mạng
- Đặt `ADMIN_PASSWORD` mạnh trong `.env`. Nếu để trống, mật khẩu mặc định là `admin123`.
- Chạy sau HTTPS (Nginx, Caddy hoặc hosting có sẵn HTTPS), vì mật khẩu admin đi qua mạng.
- Sao lưu thư mục `data/` định kỳ. Phiên đăng nhập lưu trong bộ nhớ nên khởi động lại máy chủ là phải đăng nhập lại.
