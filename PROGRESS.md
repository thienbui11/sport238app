# Tiến độ – SPORT 238

Cách làm tiếp: đọc tệp này → `CLAUDE.md` → `AUDIT.md` → `PROPOSALS.md`. Quy trình 7 giai đoạn do chủ shop đặt (khảo sát → đề xuất, **dừng chờ duyệt** → sửa lỗi → giao diện, **dừng chờ duyệt** → chức năng mới → nhập hàng Sapo → kiểm thử/CI → đưa lên mạng). Sau mỗi việc: kiểm thử, cập nhật tệp này, commit.

## Đang ở đâu (cập nhật 24/11/2026)
- **Giai đoạn 0 – Khảo sát:** xong. Kết quả trong `AUDIT.md`, ảnh trong `screenshots/before/khao-sat-24-11/`.
- **Sửa lỗi bắt buộc (đợt 1, chủ shop yêu cầu trực tiếp):** xong. Xem mục "Đã xong".
- **Giai đoạn 1 – Đề xuất:** `PROPOSALS.md` đã lập. **ĐANG DỪNG CHỜ CHỦ SHOP DUYỆT.** Sau khi duyệt: lập `PLAN.md` theo đúng các mục được chọn, mỗi việc có tiêu chí "xong khi…".

## Đã xong
| Ngày | Việc | Kiểm thử |
|---|---|---|
| 24/11 | Khảo sát Giai đoạn 0 (`AUDIT.md`, 32 ảnh) | – |
| 24/11 | Điện thoại: lưới 2 cột, 20 SP mỗi lần + "Xem thêm", phần đầu gọn, danh mục vuốt ngang. SP đầu tiên 3.908 → 1.156 px; trang 119.543 → 8.458 px | test_mobile |
| 24/11 | Menu ☰ cho màn hình ≤ 1000 px | test_mobile |
| 24/11 | Tìm kiếm không dấu, tìm theo mã SKU, hãng, màu | test_mobile |
| 24/11 | Quay lại (nút Back, nút "← Tất cả sản phẩm") về đúng chỗ đang xem | test_mobile |
| 24/11 | Bỏ nút Zalo nổi che nút: điện thoại có thanh dưới "Nhắn Zalo / Giỏ hàng"; 861–1339 px nút Zalo trên thanh đầu trang; ≥ 1340 px nút nổi nằm ngoài vùng SP | test_mobile |
| 24/11 | Nút size, màu, +/−, đóng giỏ, chọn danh mục… ≥ 44 px | test_mobile |
| 24/11 | Giữ màu và size đã chọn trên thẻ khi sang trang chi tiết (và ngược lại); trang chi tiết chọn sẵn màu còn hàng | test_mobile, test_feat |
| 24/11 | Hỏi lại trước khi xóa giỏ hàng | test_feat, test_mobile |
| 24/11 | Vượt tồn kho: không chặn, cảnh báo + ghi chú trong tin nhắn (quyết định của chủ shop) | test_cards, test_mobile |
| 24/11 | Giờ mở cửa 8:00–21:00 hằng ngày: thanh trên, menu, Về shop, Cách mua, giỏ, trang chi tiết, chân trang | test_mobile |
| 24/11 | Giỏ hàng là hộp thoại: con trỏ vào giỏ, Tab quay vòng, giỏ đóng thì không Tab vào được; nhãn đọc màn hình cho nút giỏ, +/−, size | test_mobile |
| 24/11 | Trang quản trị: nút Đăng xuất hoạt động (`POST /api/admin/logout` cho máy chủ Node; dọn phiên hết hạn) | test_mobile |
| 24/11 | Chế độ tối: chữ trắng trên nút đỏ đạt 4,55:1 | test_mobile |
| 24/11 | Ảnh trước–sau: `screenshots/so-sanh.html` | – |

Bỏ dải "Mới cập nhật – Hàng đang có sẵn" (trùng với danh sách, nhãn "mới" không đúng). Danh sách sản phẩm nay nằm ngay sau danh mục.

## Kết quả kiểm thử gần nhất (24/11/2026) – đều "KẾT QUẢ: 0 lỗi"
| Nơi chạy | test_all | test_feat | test_cards | test_mobile (sáng + tối) |
|---|---|---|---|---|
| Máy chủ Node `localhost:3000` (dữ liệu mẫu sạch) | 0 | 0 | 0 | 0 (kèm phần đăng xuất quản trị) |
| Web tĩnh (xuất bằng `export_static.py`) | 0 | 0 | 0 | 0 |
| Next.js `localhost:3100` | 0 | 0 | 0 | 0 |

## Việc tiếp
1. Chờ chủ shop duyệt `PROPOSALS.md`, rồi lập `PLAN.md`.
2. Ba việc chủ shop đã yêu cầu, xếp "Làm ngay" trong PROPOSALS: công cụ nạp ảnh hàng loạt theo SKU; danh mục mới "Giày thể thao" (Python + Java + CLAUDE.md); trang bảng size (dữ liệu từ các bảng chủ shop gửi, chỗ nào thiếu để trống).
3. Thư mục `sport-shop-app/dist/` (bản để đưa lên hosting) **chưa xuất lại** theo giao diện mới. Lần bấm `cap-nhat-web.bat` tới sẽ tự xuất lại; hoặc chạy `npm start` rồi `python tools\daily_update.py --export-only`.

## Lỗi còn lại (chi tiết trong `AUDIT.md`)
- L14 địa chỉ lỗi mã hóa làm máy chủ Node báo 500 (nhẹ).
- L15 "Hỏi shop về sản phẩm này" chưa kèm tên sản phẩm.
- L16 link sản phẩm chia sẻ không hiện đúng sản phẩm; Google không đọc được từng sản phẩm.
- L17 trang quản trị bản Node nhận `.xlsx` nhưng báo lỗi chung chung.
- Chưa có pytest cho bộ đọc Excel Python; chưa có kiểm thử trang quản trị (ngoài đăng xuất).

## Lệnh tự kiểm tra
```
# 1) máy chủ Node với dữ liệu mẫu sạch (không đụng dữ liệu thật): đặt DATA_DIR sang thư mục tạm có seed-products.json
cd sport-shop-app && py tools/build_storefront.py && npm start
py tests/test_all.py http://localhost:3000      # tương tự test_feat, test_cards, test_mobile
# 2) web tĩnh
py tools/export_static.py --out <thư mục tạm> ; py -m http.server 8098 --directory <thư mục tạm> ; chạy 4 bài với http://localhost:8098
# 3) Next.js (TẮT máy chủ cũ trước khi build)
cd sport-shop-next/frontend && rm -rf .next && npm run build && npx next start -p 3100 ; chạy 4 bài với http://localhost:3100
# 4) ảnh trước–sau: mở screenshots/so-sanh.html
```
Trên máy này lệnh Python là `py` (hoặc `python` trong cửa sổ mở sau khi cài Python).

## Cần hỏi chủ shop
- Duyệt `PROPOSALS.md` (chọn mục nào làm).
- Thư mục ảnh sản phẩm cụ thể (ví dụ `D:\anh-san-pham`) khi đã gom xong 20–30 sản phẩm bán chạy.
- Bảng size giày (chưa có trong các bảng đã gửi), bảng size cho các hãng khác đang bán (Wika, Mira, Peace Max, CV, HD Sport…), nếu có.
- Thẻ tích điểm (mỗi 100k một ô, quà theo số ô): có muốn ghi lên web không, và áp dụng thế nào cho khách đặt qua web.
- Tạo tệp `sport-shop-app/.env` với mật khẩu quản trị mạnh (để nút cập nhật nhập được Excel).

---
## Ghi chú cũ

### Next.js 16 và cảnh báo PostCSS
Đã nâng `sport-shop-next/frontend` lên Next.js 16.4.6 (24/11/2026), `npm audit` 0 lỗi; nhãn trước khi nâng: `ban-on-dinh-2026-11-24`, sau khi nâng: `ban-on-dinh-next16`. Cảnh báo PostCSS (GHSA-6g55-p6wh-862q, GHSA-r28c-9q8g-f849, GHSA-qx2v-qp2m-jg93, GHSA-fxqj-rqcc-2cmp) chỉ ở Next.js 15 và chỉ chạy lúc build; web tĩnh đang bán không dùng npm nên không bị ảnh hưởng.

### Công cụ trên máy (24/11/2026)
| Công cụ | Tình trạng | Cần cho việc gì |
|---|---|---|
| Node.js | Có (v26) | Trang quản trị, build Next.js |
| Python | Đã cài 3.15.2, có pandas, openpyxl, pillow, playwright | Bắt buộc cho cập nhật hằng ngày |
| Java 21 + Maven | Chưa cài (lần trước dùng bản di động trong thư mục tạm) | Backend Spring Boot, đối chiếu `SapoParser` |
| Docker Desktop | Bị treo | Backend + PostgreSQL |

`python tools\daily_update.py --export-only` chạy được; đọc file Sapo thật 14/11/2026 ra đúng 175 SP, 953 phiên bản, bỏ 68 phiên bản giá 0. Chromium của Playwright ở `C:\Users\Admin\AppData\Local\ms-playwright`.
