# SPORT 238 – web bán đồ thể thao (hướng dẫn cho Claude Code)

Đọc kỹ file này trước khi sửa. Người dùng là chủ shop, không phải lập trình viên: trả lời bằng tiếng Việt, giải thích ngắn gọn, và **tự chạy kiểm thử, sửa lỗi rồi mới báo kết quả**.

## Quy tắc kinh doanh (không được phá)
- Cửa hàng: **SPORT 238 – KCN An Hiệp**, 238 ấp Thuận Điền, xã Phú Túc, tỉnh Vĩnh Long (Ngã 3 KCN An Hiệp). Zalo 0962374770. Facebook `facebook.com/Sport238` (Messenger `m.me/Sport238`). Tên Facebook có thể nhập cả đường dẫn; luôn chuẩn hóa về tên trang.
- Web **chỉ hiển thị sản phẩm**. Khách chọn size/màu, thêm giỏ, **sao chép đơn** rồi nhắn shop qua Zalo/Messenger. Không thanh toán online.
- **Shop không giao hàng.** Không dùng chữ "ship", "giao hàng", "phí giao", "gửi hàng". Luôn ghi **"ghé shop nhận hàng"** (kèm địa chỉ).
- **Giờ mở cửa: 8:00–21:00, tất cả các ngày trong tuần** (chủ shop xác nhận 24/11/2026). Sửa ở `CFG.hours` trong `storefront.template.html` và `HOURS` trong `sport-shop-next/frontend/lib/shop.ts`.
- **Không chặn cứng khi đặt vượt tồn kho** (chủ shop quyết định 24/11/2026): vẫn cho thêm vào giỏ, hiện cảnh báo "Số lượng vượt tồn kho trên web, shop sẽ kiểm tra lại khi chốt đơn", tin nhắn gửi shop có ghi chú. Biến thể tồn 0 thì vẫn không thêm được (ghi "Tạm hết hàng").
- Dữ liệu hàng lấy từ **Sapo POS** bằng file Excel (nút "Xuất file"), **không có API**. Tồn kho là ảnh chụp theo đợt (ghi "Tồn kho cập nhật ngày …", shop xác nhận khi chốt đơn).
- **Tuyệt đối không đưa giá nhập, giá vốn, giá buôn lên web.** Bộ đọc Excel chỉ đọc giá bán lẻ và tồn kho. Đừng thêm các cột khác vào API công khai.
- Shop còn bán đồ mẹ và bé trong cùng Sapo: các sản phẩm đó phải bị loại (xem `classify`).
- 9 danh mục: Cờ, Cúp, Huy Chương · Giày bóng đá · **Giày thể thao** (giày vải, thể dục, thể thao không phải giày đá bóng; chủ shop duyệt 24/11/2026) · Quần áo CLB/Đội tuyển · Quần áo không logo · Quần áo trẻ em · Phụ kiện thể thao · Vớ/tất ống đồng · Cầu lông. Người dùng có thể chọn tay danh mục trong trang quản trị (không bị ghi đè khi nhập lại Excel).
- Giao diện: tiếng Việt, màu theo logo (đỏ đô + xám đen), dùng được trên điện thoại, có chế độ tối, bàn phím và trình đọc màn hình dùng được.

## Cấu trúc
- `sport-shop-app/` – **trang quản trị + API** chạy trên máy shop: máy chủ Node không cần thư viện (Node ≥ 22.9, SQLite có sẵn), `/admin`. Là nguồn dữ liệu khi xuất web. Công cụ: nhập Excel Sapo, nạp ảnh, cập nhật hằng ngày, xuất web tĩnh (`dist/`). Hướng dẫn vận hành: `sport-shop-app/HUONG-DAN-DUA-LEN-MANG.md`.
- `sport-shop-next/frontend/` – **giao diện cửa hàng CHÍNH** (Next.js 16, TypeScript). Xuất web tĩnh bằng `py sport-shop-app/tools/export_next.py` (biến `XUAT_TINH=1`): mỗi sản phẩm một trang `/san-pham/<MÃ>/` có tiêu đề, mô tả, Open Graph, JSON-LD; sitemap khi có `SITE_URL`.
- `sport-shop-next/backend/` – Spring Boot 3.5, Java 21, PostgreSQL (chưa dùng để bán). Bộ đọc Excel Java phải giống bản Python.
- `tests/` – kiểm thử bằng Chromium thật (Playwright) và pytest (`tests/py`). Xem `tests/README.md`.

## Hai bản giao diện: Next.js là bản chính, HTML là bản dự phòng (chủ shop duyệt E2, 24/11/2026)
- **Chức năng mới, giao diện mới: chỉ làm trên bản Next.js** (`sport-shop-next/frontend`). Nút cập nhật hằng ngày xuất bằng Next.js; build lỗi (ví dụ mất mạng khi tải phông chữ) hoặc chưa `npm install` thì tự dùng bản HTML (`XUAT_WEB=html` trong `.env` để luôn dùng HTML).
- **Bản HTML** (`sport-shop-app/tools/storefront.template.html` → `public/index.html` bằng `build_storefront.py`, không sửa tay `public/index.html`) giữ nguyên làm dự phòng: chỉ sửa lỗi; vẫn phải đạt 4 bài kiểm thử cơ bản. **Chưa xóa** – xóa hẳn phải hỏi chủ shop.
- Hai bản giữ chung các mã kiểm thử (`#grid .card`, `.szb`, `.clb`, `[data-quick]`, `#cb`, `#dr`, `#ordtxt`, `#more`, khóa giỏ `cart5`…) để 4 bài kiểm thử cơ bản chạy được trên cả hai.
- CSS: bản Next.js dùng `sport-shop-next/frontend/app/globals.css` (tự do làm lại giao diện). Bản HTML dự phòng dùng CSS riêng đã chốt `sport-shop-app/tools/storefront.css` (24/11/2026); chỉ sửa khi sửa lỗi bản dự phòng.
- Trang quản trị: `sport-shop-app/public/admin.html`, bản sao `sport-shop-next/frontend/public/admin/index.html` (giữ giống hệt; không có trong web xuất tĩnh).
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
- Giao diện cửa hàng: chạy **bốn** bài trong `tests/` (`test_all`, `test_feat`, `test_cards`, `test_mobile`; xem `tests/README.md`) trên máy chủ Node (3000), web tĩnh và Next.js (3100); phải ra "KẾT QUẢ: 0 lỗi". `test_mobile` chạy cả chế độ sáng lẫn tối và đo tương phản, cỡ nút ≥ 44 px.
- Danh sách hiện 20 sản phẩm mỗi lần (nút "Xem thêm" `#more button`): bài kiểm thử nào cần đếm toàn bộ thì gọi `show_all(pg)` trước.
- Build lại Next.js: **tắt máy chủ `next start` trước**, xóa `.next`, rồi build; máy chủ cũ còn chạy sẽ ghi đè trang cũ vào `.next` (trang chi tiết mất CSS).
- Sửa quy tắc đọc Excel: đối chiếu Python và Java như trên.
- Mở trình duyệt xem thật những chỗ vừa sửa (ảnh chụp, điện thoại 390 px, chế độ tối).
- Trước khi kiểm thử, xem cổng đã trống chưa (`netstat -ano | findstr :3100`). Trên Windows, tắt cửa sổ lệnh có thể để sót tiến trình `node` vẫn phát bản build cũ, gây lỗi giả ("module factory is not available", bấm nút không ăn). Tắt hẳn bằng số tiến trình (PID).

## Tình trạng hiện tại và việc nên làm tiếp
1. `sport-shop-next/frontend` đã nâng lên Next.js 16.4.6 (24/11/2026; `npm audit` 0 lỗi), build và đạt cả ba bài kiểm thử Playwright (chạy `npx next start -p 3100` rồi dùng `http://localhost:3100`). Bản React dùng cùng `id`/`data-*`, cùng khóa giỏ `cart5` (`[{id,lb,qty}]`) và có `/products.json` như bản HTML; đường dẫn cũ `/#p-MÃ` tự chuyển sang `/san-pham/MÃ`. Khi sửa giao diện, giữ các mã này ở cả hai bản.
2. `sport-shop-next/backend` đã biên dịch, `mvn test` đạt (24/11/2026). Chưa chạy thật với PostgreSQL (`docker compose up`).
3. Kế hoạch theo giai đoạn: xem `PROGRESS.md` (việc đang làm, việc tiếp), `AUDIT.md` (khảo sát, lỗi), `PROPOSALS.md` (đề xuất chờ chủ shop duyệt), `screenshots/so-sanh.html` (trước–sau).
4. Ảnh sản phẩm: chủ shop sẽ gom ảnh vào một thư mục, đặt tên theo mã SKU (`PVN3939.jpg`, `PVN3939-1.jpg`…); cần công cụ nạp hàng loạt (tự thu nhỏ, đổi WebP, báo SP chưa có ảnh).
5. Đưa lên mạng: đề xuất Cloudflare Pages cho web tĩnh (Vercel gói miễn phí chỉ cho phi thương mại nên không dùng). Người dùng tự lo tài khoản, tên miền. Chưa xác nhận thủ tục thông báo website theo Luật Thương mại điện tử 2025 và Nghị định 248/2026/NĐ-CP: nhắc người dùng hỏi Sở Công Thương.
6. Tự động hóa lấy dữ liệu Sapo cần API của Sapo (chưa có). Khi có, thay bước xuất Excel trong `tools/daily_update.py`.

## Việc không nên làm
- Không đưa trang quản trị lên mạng công khai khi chưa có HTTPS và mật khẩu mạnh (`ADMIN_PASSWORD` mặc định `admin123` chỉ để thử).
- Không commit `.env`, `data/shop.db*`, `data/uploads`, `dist`.
- Không thêm thư viện nặng cho bản `sport-shop-app` (cố ý không có phụ thuộc).
