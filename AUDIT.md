# AUDIT – Khảo sát web SPORT 238 (Giai đoạn 0, ngày 24/11/2026)

Phạm vi: bản đang bán `sport-shop-app` (web tĩnh `dist/` + trang quản trị), có đối chiếu bản `sport-shop-next`.
Theo yêu cầu của chủ shop, đợt này **không** cài, build hay chạy lại kiểm thử cũ (đã đạt trước đó) và **không** chạy backend Spring Boot (máy chưa có Java, Maven; Docker bị treo).
Cách làm: đọc mã, mở web bằng Chromium thật (Playwright) ở 1366 px và 390 px, sáng và tối, đo tự động.

Ảnh hiện trạng ban đầu: `screenshots/before/khao-sat-24-11/` (32 ảnh). Ảnh so sánh: `screenshots/before/`, `screenshots/after/`, trang `screenshots/so-sanh.html`.
Tên ảnh khảo sát: `số-nội dung-thiết bị-chế độ`, với `pc` là máy tính, `dt` là điện thoại.

## a) Bản đồ chức năng

HTML = `sport-shop-app/tools/storefront.template.html` (dựng ra `public/index.html`). React = `sport-shop-next/frontend/components/…`. CSS dùng chung: `sport-shop-next/frontend/app/globals.css`.

| Chức năng | Bản HTML (hàm) | Bản React | Kiểm thử |
|---|---|---|---|
| Tải dữ liệu, chuẩn hóa sản phẩm | `build()`, `get()` | `lib/shop.ts` `getCatalog()` | test_all (175 SP), test_cards |
| Trang chủ: phần mở đầu, số liệu, danh mục | `home()` | `app/page.tsx`, `Shop.tsx` | test_all (8 ô danh mục, số SP) |
| Danh sách: lọc danh mục, tình trạng, sắp xếp | `matches()`, `list()`, `cmp()` | `Shop.tsx` `Storefront` | test_all (đếm theo danh mục) |
| Tìm kiếm không dấu, theo mã, hãng, màu | `fold()`, `p.key` | `lib/shop.ts` `fold`, `key` | **test_mobile** (mới) |
| Xem thêm (20 SP mỗi lần) | `list()`, `#moreb` | `Storefront` | **test_mobile** |
| Thẻ SP: chọn màu, size, tồn kho, thêm giỏ | `card()`, trình nghe `click` | `Shop.tsx` `Card` | test_cards, test_feat |
| Trang chi tiết: ảnh, màu, size, tồn từng size | `detail()` | `ProductDetail.tsx`, `app/san-pham/[id]` | test_all (175 trang), test_cards |
| Giữ màu/size giữa thẻ và trang chi tiết | `CS`, `cst()`, `keep()` | `Providers` `picks` | **test_mobile**, test_feat |
| Quay lại đúng chỗ đang xem | `route()`, `RET` | `Providers` `ret`, `Storefront` | **test_mobile** |
| Giỏ hàng: số lượng, tạm tính, lưu máy | `add()`, `renderCart()`, `cart5` | `Providers`, `CartDrawer.tsx` | test_all, test_feat |
| Cảnh báo vượt tồn kho (không chặn) | `add()`, `OVER` | `Providers` `add` | test_cards, **test_mobile** |
| Hỏi lại trước khi xóa giỏ | `#cc`, `#ccq` | `CartDrawer` | test_feat, **test_mobile** |
| Sao chép đơn, mở Zalo/Messenger, dự phòng clipboard | `copyText()`, `afterCopy()` | `CartDrawer` `copyText` | test_feat |
| Menu điện thoại | `menu()` | `Header.tsx` | **test_mobile** |
| Thanh dưới (Zalo, giỏ) trên điện thoại | `#bbar` | `Header.tsx` `BottomBar` | **test_mobile** |
| Giờ mở cửa | `CFG.hours` | `lib/shop.ts` `HOURS` | **test_mobile** |
| Bàn phím trong giỏ (vào giỏ, Tab quay vòng) | `drawer()` | `CartDrawer` | **test_mobile** |
| Link Facebook/Zalo chuẩn hóa | `fbUser()`, `applyCfg()` | `lib/shop.ts` `fbUser`, `links` | test_all |
| Máy chủ, API công khai, đăng nhập, đăng xuất | `src/server.js` | Spring Boot `PublicController`, `AdminController` | test_mobile (đăng xuất); Java: `mvn test` |
| Trang quản trị: sửa SP, ảnh, danh mục, cài đặt | `public/admin.html` (bản sao ở `frontend/public/admin/index.html`) | dùng chung | **chưa có** → nay có `tests/test_admin.py` (24/11) |
| Tải ảnh lên (nhận dạng ảnh, thu nhỏ) | `server.js` `sniff()`, `admin.html` `shrinkImg()` | `ImageStorageService` | **chưa có** |
| Đọc Excel Sapo, phân loại, gộp size | `tools/sapo_xlsx_to_json.py` | `SapoParser.java` | Java: `mvn test`; Python: **chưa có pytest** |
| Cập nhật hằng ngày | `tools/daily_update.py`, `cap-nhat-web.bat` | – | **chưa có** |
| Xuất web tĩnh | `tools/export_static.py` | – | gián tiếp (chạy 4 bài trên `dist`) |

## b) Lỗi (mức độ, cách tái hiện, tình trạng)

| # | Lỗi | Mức | Cách tái hiện | Ảnh | Tình trạng |
|---|---|---|---|---|---|
| L1 | Điện thoại: 1 SP mỗi hàng, trang dài 119.543 px, SP đầu tiên ở 3.908 px, "Về shop" ở khoảng 117.600 px | Nghiêm trọng | Mở web ở 390 px, cuộn | `khao-sat-24-11/07-luoi-sanpham-dt.jpg` | **Đã sửa**: 2 cột, xem thêm 20 SP, trang 8.458 px, SP đầu ở 1.156 px |
| L2 | Dưới 1000 px không có menu | Nghiêm trọng | Mở ở 390 px: không có nút điều hướng | `01-trangchu-dt-light.jpg` | **Đã sửa**: menu ☰ |
| L3 | Tìm "giay" ra 0 (phải gõ "giày"); không tìm theo mã, hãng | Nghiêm trọng | Gõ "giay" vào ô tìm | `06-timkhongthay-*.jpg` | **Đã sửa**: không dấu, theo mã, hãng, màu |
| L4 | Xem chi tiết rồi quay lại thì mất chỗ (23.049 → 3.275 px) | Vừa | Cuộn tới SP thứ 31, mở, bấm Back hoặc "← Tất cả sản phẩm" | – | **Đã sửa** cả hai cách quay lại |
| L5 | Nút Zalo nổi che nút "Thêm vào giỏ", nút size, nút chọn loại ở trang chi tiết | Vừa | 390 px, cuộn danh sách; mở SP PVN3632 | `04-chitiet-nhieumau-dt-light.jpg` | **Đã sửa**: thanh dưới trên điện thoại, nút Zalo lên thanh đầu trang ở 861–1339 px |
| L6 | Màu chọn trên thẻ không sang trang chi tiết; trang chi tiết chọn sẵn màu đã hết | Vừa | Chọn "Vàng" trên thẻ, mở chi tiết → "Xanh cổ vịt" | – | **Đã sửa** (giữ cả size) |
| L7 | Nút size/màu trên thẻ cao khoảng 24 px | Vừa | Đo ở 390 px | `09-chua-chon-size-dt.jpg` | **Đã sửa**: tối thiểu 44 px (cả +/−, nút đóng giỏ) |
| L8 | "Xóa giỏ hàng" xóa ngay, không hỏi | Vừa | Mở giỏ, bấm Xóa giỏ hàng | – | **Đã sửa**: hỏi lại, mặc định "Giữ lại" |
| L9 | Trang quản trị: "Đăng xuất" không có tác dụng (cookie HttpOnly) | Vừa | Đăng nhập, Đăng xuất, tải lại: vẫn vào được | – | **Đã sửa**: `POST /api/admin/logout` (bản Java đã có sẵn) |
| L10 | Giỏ đóng nhưng phím Tab vẫn đi qua 4 nút vô hình; mở giỏ không đưa con trỏ vào giỏ | Vừa | Tab từ chân trang | – | **Đã sửa** (giỏ là hộp thoại, Tab quay vòng) |
| L11 | Thông báo nhanh che giá và nút | Nhẹ | Bấm Thêm vào giỏ khi chưa chọn size | `09-chua-chon-size-dt.jpg` | **Đã sửa**: điện thoại hiện ở đầu màn hình |
| L12 | Chế độ tối: chữ trắng trên nút đỏ 4,497:1 (dưới chuẩn 4,5) | Nhẹ | Đo tương phản | – | **Đã sửa**: 4,55:1 |
| L13 | Không có giờ mở cửa ở đâu cả | Vừa | – | – | **Đã sửa**: 8:00–21:00 hằng ngày (chủ shop cung cấp) |
| L14 | Địa chỉ web lỗi mã hóa (`/%E0`) làm máy chủ Node báo lỗi 500 | Nhẹ | `curl localhost:3000/%E0` | – | **Đã sửa**: trả 400 (tests/py/test_server.py) |
| L15 | "Hỏi shop về sản phẩm này" mở Messenger trống, khách phải gõ lại tên SP | Nhẹ | Bấm nút ở trang chi tiết | – | Chưa sửa (đưa vào PROPOSALS) |
| L16 | Link sản phẩm `/#p-…` chia sẻ chỉ hiện tiêu đề chung; Google không đọc được từng SP | Vừa | Dán link vào Zalo | – | Chưa sửa (PROPOSALS, kiến trúc) |
| L17 | Admin cho chọn `.xlsx` nhưng máy chủ Node chỉ nhận JSON, báo lỗi chung chung | Nhẹ | Tab Nhập từ Sapo, chọn .xlsx | – | **Đã sửa**: báo rõ dùng cap-nhat-web.bat (tests/py/test_server.py) |
| L18 | Danh mục "Giày bóng đá" lẫn giày vải, giày thể thao | Vừa | Xem danh mục | – | Chủ shop đã duyệt thêm "Giày thể thao" (PROPOSALS) |

## c) Vấn đề trải nghiệm còn lại
- **0/175 sản phẩm có ảnh thật, 0/175 có mô tả.** Mọi thẻ là emoji giống nhau theo danh mục; trong chế độ tối nền màu nhạt bị chói.
- Chưa có bảng size (chủ shop đã gửi bảng của các hãng).
- 44/175 sản phẩm (25%) hết hàng vẫn hiện (xếp cuối).
- Nút "Sao chép đơn hàng" trong giỏ xuống 2 dòng trên điện thoại.

## d) Đánh giá giao diện
- **Tốt:** màu đỏ đô và đen đúng logo, nhất quán; phần mở đầu trên máy tính mạnh; chữ dễ đọc (Be Vietnam Pro); chế độ tối đồng bộ; tôn trọng "giảm chuyển động"; nội dung đơn hàng rõ, có mã từng món.
- **Cần làm (Giai đoạn 3):** chưa có hệ thống thiết kế (màu, cỡ chữ, khoảng cách khai báo rải rác, CSS vá chồng nhiều lớp); thẻ sản phẩm phụ thuộc ảnh thật; trang chi tiết chưa có bảng size, sản phẩm liên quan; cảm giác "thể thao" mới nằm ở phần mở đầu.

## e) Nợ kỹ thuật và bảo mật
| # | Vấn đề | Mức |
|---|---|---|
| N1 | Hai bản giao diện (HTML thuần, React) phải sửa tay cho giống nhau; chỉ 4 bài Playwright giữ cho hai bản khớp | Cao |
| N2 | Hai bộ đọc Excel (Python, Java) phải giống hệt; Python chưa có pytest; Java chưa chạy được trên máy này | Cao |
| N3 | `globals.css` vá chồng nhiều lớp, có CSS thừa (`.pal`, `.art .e4`, `.sz u`, `.df small`) | Vừa |
| N4 | `index.html` 139 KB, trong đó 78 KB là logo nhúng 3 lần; `logo.png` 118 KB | Vừa |
| N5 | Trang tải cấu hình xong mới tải sản phẩm (hai lượt chờ nối tiếp) | Thấp |
| N6 | `products.json` công khai có trường nội bộ không cần (`active`, `hidden`, `category_auto`, `category_override`, `product_type`). **Không có giá nhập, giá vốn**: mỗi phiên bản chỉ có `id, sku, option1, option2, price, inventory_quantity` | Thấp |
| N7 | Phiên đăng nhập trong bộ nhớ (khởi động lại là mất); bộ đếm sai mật khẩu không được dọn. Đã thêm dọn phiên hết hạn | Thấp |
| N8 | `ADMIN_PASSWORD` mặc định `admin123` khi thiếu `.env`; chưa có tệp `.env` trên máy | Vừa (chỉ chạy trên máy shop) |
| N9 | Tài liệu lệch: `sport-shop-next/README.md` ghi 932 phiên bản, CLAUDE.md ghi 953 | Thấp |
| N10 | Khi build lại Next.js mà máy chủ cũ còn chạy, máy chủ cũ ghi đè trang cũ vào `.next` (trang mất CSS). Luôn tắt máy chủ trước khi build | Thấp |

**Rút lại một nhận định ban đầu:** `cap-nhat-web.bat` không hỏng. Lệnh `python` chỉ trỏ vào lối tắt Microsoft Store trong các cửa sổ mở từ trước khi cài Python; PATH mới đã đặt Python 3.15 lên trước.
