# SPORT 238 – Next.js + Spring Boot + PostgreSQL

Trạng thái (24/11/2026): **frontend đã `npm run build` và đạt ba bài kiểm thử Playwright; backend đã biên dịch và `mvn test` đạt.** Backend chưa chạy thật với PostgreSQL.
Đã kiểm tra: cú pháp toàn bộ tệp TypeScript, logic xử lý dữ liệu (`lib/shop.ts`), và bộ đọc file Sapo (`SapoParser`) với file Excel thật (632 sản phẩm trong file, 175 lên web, 932 phiên bản).

> **Muốn bán ngay, chưa cần backend?** Dùng gói `sport-shop-app` (web tĩnh + trang quản trị chạy trên máy shop). Xem `HUONG-DAN-DUA-LEN-MANG.md` trong gói đó. Gói `sport-shop-next` này dành cho giai đoạn sau (mỗi sản phẩm có địa chỉ riêng cho Google, đơn hàng, tồn kho tức thì).

## Chạy backend
Cần Docker. Trong thư mục này:

    cp .env.example .env     # sửa mật khẩu
    docker compose up --build

API tại http://localhost:8080 . Muốn chạy không dùng Docker: cần JDK 21, Maven, một PostgreSQL, rồi `cd backend && mvn spring-boot:run`
(biến môi trường: DB_URL, DB_USER, DB_PASSWORD, ADMIN_PASSWORD...). Chạy kiểm thử: `mvn test`.

## Chạy frontend (Next.js)
Cần Node.js 20 trở lên.

    cd frontend
    cp .env.example .env
    npm install
    npm run dev            # http://localhost:3000

- **Cách A (hiện tại):** để trống `API_URL`. Web đọc `frontend/data/products.json`. Cập nhật hàng: xuất Excel từ Sapo, chạy `python tools/sapo_xlsx_to_json.py file.xlsx` (ghi thẳng vào `frontend/data/products.json`, cần `pip install pandas openpyxl`), rồi build lại hoặc triển khai lại.
- **Ảnh (cách A):** chép ảnh vào `frontend/public/products/` và khai báo trong `frontend/data/images.json`, ví dụ `{"PVN3939":["/products/giay-1.jpg"],"PVN3967:Trắng-Navy Sen":["/products/amac.jpg"]}` (khóa có `:Màu` là ảnh riêng theo màu).
- **Khi backend chạy:** đặt `API_URL=http://localhost:8080`. Web lấy dữ liệu từ backend (làm mới mỗi 60 giây) và trang **/admin** dùng được: thêm ảnh, sửa tên hiển thị và mô tả, ẩn hoặc đánh dấu nổi bật, nhập thẳng file Excel Sapo.
- **Màu sắc:** các biến CSS ở đầu `frontend/app/globals.css` (đỏ đô theo logo). **Thông tin shop** (tên, Zalo, địa chỉ): `DEFAULT_SITE` trong `frontend/lib/shop.ts`. **Tên Facebook cho Messenger:** `NEXT_PUBLIC_MESSENGER_USER` trong `.env` (hiện là giá trị tạm, cần điền tên trang thật).

## Thử nhanh bằng dòng lệnh

    curl http://localhost:8080/api/products
    curl -c cj -X POST -H 'Content-Type: application/json' -d '{"password":"MẬT_KHẨU_ADMIN"}' http://localhost:8080/api/admin/login
    curl -b cj -F file=@danh_sach_san_pham.xlsx http://localhost:8080/api/admin/import
    curl -b cj --data-binary @anh.jpg http://localhost:8080/api/admin/upload

## API (giữ nguyên tên trường như bản Node đã demo)
| Đường dẫn | Mô tả |
|---|---|
| GET /api/products | sản phẩm đang bán + ảnh |
| GET /api/config | tên shop, Messenger, Zalo |
| POST /api/admin/login, /logout · GET /api/admin/me | đăng nhập bằng session (sai quá 5 lần thì khóa 10 phút) |
| GET /api/admin/products | toàn bộ sản phẩm kể cả đang ẩn |
| POST /api/admin/import | tải file .xlsx từ Sapo (multipart, trường `file`) |
| PUT /api/admin/products/{id} | sửa thông tin chỉ có trên web: `display_title`, `description`, `hidden`, `featured` (không bị ghi đè khi nhập lại từ Sapo) |
| POST /api/admin/images | `{product_id, color, urls[]}` |
| POST /api/admin/upload | tải ảnh (gửi thẳng nội dung tệp; JPG/PNG/WEBP/GIF, tối đa 8MB) |
| POST /api/admin/config | lưu tên shop, Messenger, Zalo |

## Cấu trúc backend
    config/    ShopProperties (cấu hình), SecurityConfig (đăng nhập admin), WebConfig (phục vụ /uploads)
    service/   SapoParser (đọc Sapo, Java thuần), ExcelImportService (POI), CatalogService (truy vấn),
               ConfigService, ImageStorageService
    web/       PublicController, AdminController, ApiExceptionHandler
    resources/ application.yml, db/migration/V1__init.sql, V2__product_web_info.sql (Flyway tự tạo bảng)

Truy cập dữ liệu dùng Spring JDBC (JdbcTemplate) cho đơn giản. Khi thêm nhiều bảng phức tạp (đơn hàng, khách), có thể thêm Spring Data JPA.

## Lộ trình tiếp theo
4. Lưu đơn hàng · 5. Docker Compose đủ 3 dịch vụ (thêm frontend) + hướng dẫn triển khai.

## Lưu ý
- Đặt `ADMIN_PASSWORD` mạnh; nếu để trống, mật khẩu là `admin123` (chỉ để chạy thử).
- Khi chạy sau HTTPS, đặt `COOKIE_SECURE=true`.
- Next.js sẽ gọi API qua `rewrites` (cùng tên miền), nên cookie đăng nhập hoạt động mà không cần CORS.
- **Danh mục:** web tự xếp sản phẩm vào 8 danh mục theo tên và loại (xem hàm `classify` trong `tools/sapo_xlsx_to_json.py` và `SapoParser.java`, hai nơi có logic giống hệt nhau). Muốn chuyển một sản phẩm sang danh mục khác, chọn tay trong /admin (không bị ghi đè khi nhập lại từ Sapo). Sản phẩm không phải đồ thể thao (đồ mẹ và bé) tự bị loại.
- **Gộp size:** nhiều sản phẩm trong Sapo mỗi size là một sản phẩm riêng (tên có "Size 42", "- XL"). Công cụ tách size khỏi tên và gộp thành một sản phẩm nhiều size để khách chọn size ở trang chi tiết.
