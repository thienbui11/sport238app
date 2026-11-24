# SPORT 238 – web bán đồ thể thao (hướng dẫn cho Claude Code)

Đọc kỹ file này trước khi sửa. Người dùng là chủ shop, không phải lập trình viên: trả lời bằng tiếng Việt, giải thích ngắn gọn, và **tự chạy kiểm thử, sửa lỗi rồi mới báo kết quả**.

## Quy tắc kinh doanh (không được phá)
- Cửa hàng: **SPORT 238 – KCN An Hiệp**, 238 ấp Thuận Điền, xã Phú Túc, tỉnh Vĩnh Long (Ngã 3 KCN An Hiệp). Zalo 0962374770. Facebook `facebook.com/Sport238` (Messenger `m.me/Sport238`). Tên Facebook có thể nhập cả đường dẫn; luôn chuẩn hóa về tên trang.
- Web **chỉ hiển thị sản phẩm**. Khách chọn size/màu, thêm giỏ, **sao chép đơn** rồi nhắn shop qua Zalo/Messenger. Không thanh toán online.
- **Shop không giao hàng.** Không dùng chữ "ship", "giao hàng", "phí giao", "gửi hàng". Luôn ghi **"ghé shop nhận hàng"** (kèm địa chỉ).
- Dữ liệu hàng lấy từ **Sapo POS** bằng file Excel (nút "Xuất file"), **không có API**. Tồn kho là ảnh chụp theo đợt (ghi "Tồn kho cập nhật ngày …", shop xác nhận khi chốt đơn).
- **Tuyệt đối không đưa giá nhập, giá vốn, giá buôn lên web.** Bộ đọc Excel chỉ đọc giá bán lẻ và tồn kho. Đừng thêm các cột khác vào API công khai.
- Shop còn bán đồ mẹ và bé trong cùng Sapo: các sản phẩm đó phải bị loại (xem `classify`).
- 8 danh mục: Cờ, Cúp, Huy Chương · Giày bóng đá · Quần áo CLB/Đội tuyển · Quần áo không logo · Quần áo trẻ em · Phụ kiện thể thao · Vớ/tất ống đồng · Cầu lông. Người dùng có thể chọn tay danh mục trong trang quản trị (không bị ghi đè khi nhập lại Excel).
- Giao diện: tiếng Việt, màu theo logo (đỏ đô + xám đen), dùng được trên điện thoại, có chế độ tối, bàn phím và trình đọc màn hình dùng được.

## Cấu trúc
- `sport-shop-app/` – **bản đang dùng để bán**: máy chủ Node không cần thư viện (Node ≥ 22.9, SQLite có sẵn) gồm trang quản trị `/admin` và API; cửa hàng là một tệp `public/index.html`. Có công cụ xuất **web tĩnh** (`dist/`) để đưa lên hosting. Hướng dẫn vận hành: `sport-shop-app/HUONG-DAN-DUA-LEN-MANG.md`.
- `sport-shop-next/` – bản nâng cấp sau: `frontend/` (Next.js 15, TypeScript) và `backend/` (Spring Boot 3.5, Java 21, PostgreSQL, Flyway). **Cùng giao diện, cùng API, cùng quy tắc.**
- `tests/` – kiểm thử bằng Chromium thật (Playwright). Xem `tests/README.md`.

## Hai bản giao diện phải luôn đồng bộ
Giao diện cửa hàng có **hai bản cài đặt**: HTML thuần (`sport-shop-app`) và React (`sport-shop-next/frontend`). Sửa bên nào thì sửa bên kia.
- CSS **dùng chung**: `sport-shop-next/frontend/app/globals.css`.
- Bản HTML thuần được dựng từ `sport-shop-app/tools/storefront.template.html` + CSS trên + logo bằng `python sport-shop-app/tools/build_storefront.py`. **Không sửa tay `public/index.html`** (sẽ bị ghi đè); sửa mẫu rồi dựng lại.
- Trang quản trị: `sport-shop-app/public/admin.html`, bản sao nằm ở `sport-shop-next/frontend/public/admin/index.html` (giữ giống nhau).
- API công khai: `GET /api/products` (`products`, `images`, `updated`), `GET /api/config`. Trường: `id, title, display_title, description, category, vendor, featured, variants[{id,sku,option1(size),option2(màu/loại),price,inventory_quantity}]`.

## Phân loại và đọc Excel Sapo (có hai bản, phải giống hệt)
- Python: `tools/sapo_xlsx_to_json.py` (hàm `classify`, `split_size`, `label_duplicates`, `nc`). Java: `sport-shop-next/backend/.../SapoParser.java`.
- Quy tắc chính: lọc đồ thể thao theo loại Sapo + tên; tách size khỏi tên rồi **gộp** các sản phẩm "mỗi size một sản phẩm"; chuẩn hóa màu ("Navy- tím nhạt" = "Navy-tím nhạt"); biến thể trùng size và màu được gắn nhãn theo giá; bỏ biến thể giá bán lẻ = 0; tồn âm coi là 0.
- Sửa quy tắc ở một nơi thì sửa nơi kia, rồi đối chiếu kết quả hai bản trên file Excel thật (kết quả mong đợi với file ngày 14/11/2026: **175 sản phẩm, 953 phiên bản, 632 sản phẩm trong file, 68 phiên bản giá 0 bị bỏ**).

## Lệnh thường dùng
```
cd sport-shop-app
cp .env.example .env           # đặt ADMIN_PASSWORD
npm start                      # web http://localhost:3000 , quản trị /admin
python tools/sapo_xlsx_to_json.py file.xlsx out.json   # cần: pip install pandas openpyxl pillow
python tools/daily_update.py   # đọc Excel mới nhất trong inbox/, nhập vào admin, xuất dist/
python tools/export_static.py  # chỉ xuất web tĩnh
python tools/build_storefront.py
cd ../sport-shop-next/frontend && npm install && npm run dev     # Next.js
cd ../backend && mvn test && docker compose -f ../docker-compose.yml up --build
```
Muốn có dữ liệu sạch để thử: xóa `sport-shop-app/data/shop.db*` và `data/uploads`, rồi chạy lại `npm start` (tự nạp `data/seed-products.json`).

## Kiểm thử (bắt buộc trước khi báo xong)
- Giao diện cửa hàng: chạy ba bài trong `tests/` (xem `tests/README.md`); phải ra "KẾT QUẢ: 0 lỗi" trên cả máy tính lẫn điện thoại.
- Sửa quy tắc đọc Excel: đối chiếu Python và Java như trên.
- Mở trình duyệt xem thật những chỗ vừa sửa (ảnh chụp, điện thoại 390 px, chế độ tối).

## Tình trạng hiện tại và việc nên làm tiếp
1. `sport-shop-next/frontend` đã `npm install` + `npm run build` (24/11/2026) và đạt cả ba bài kiểm thử Playwright (chạy `npx next start -p 3100` rồi dùng `http://localhost:3100`). Bản React dùng cùng `id`/`data-*`, cùng khóa giỏ `cart5` (`[{id,lb,qty}]`) và có `/products.json` như bản HTML; đường dẫn cũ `/#p-MÃ` tự chuyển sang `/san-pham/MÃ`. Khi sửa giao diện, giữ các mã này ở cả hai bản.
2. `sport-shop-next/backend` đã biên dịch, `mvn test` đạt (24/11/2026). Chưa chạy thật với PostgreSQL (`docker compose up`).
3. Hỏi người dùng có giữ việc **chặn đặt quá số tồn** trong giỏ không (tồn kho có thể chưa kịp cập nhật nên có thể làm mất đơn).
4. Ảnh sản phẩm: hiện chưa có ảnh thật. Hỏi người dùng đang lưu ảnh ở đâu (thư mục máy hay link Facebook) để nạp hàng loạt.
5. Đưa lên mạng: đề xuất Cloudflare Pages cho web tĩnh (Vercel gói miễn phí chỉ cho phi thương mại nên không dùng). Người dùng tự lo tài khoản, tên miền. Chưa xác nhận thủ tục thông báo website theo Luật Thương mại điện tử 2025 và Nghị định 248/2026/NĐ-CP: nhắc người dùng hỏi Sở Công Thương.
6. Tự động hóa lấy dữ liệu Sapo cần API của Sapo (chưa có). Khi có, thay bước xuất Excel trong `tools/daily_update.py`.

## Việc không nên làm
- Không đưa trang quản trị lên mạng công khai khi chưa có HTTPS và mật khẩu mạnh (`ADMIN_PASSWORD` mặc định `admin123` chỉ để thử).
- Không commit `.env`, `data/shop.db*`, `data/uploads`, `dist`.
- Không thêm thư viện nặng cho bản `sport-shop-app` (cố ý không có phụ thuộc).
