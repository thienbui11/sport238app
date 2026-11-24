# Tiến độ và ghi chú – SPORT 238

## Cảnh báo bảo mật PostCSS (`npm audit`, kiểm tra ngày 24/11/2026)

**Nằm ở đâu:** chỉ trong `sport-shop-next/frontend`. Next.js 15.5.29 (bản mới nhất của dòng 15) đi kèm PostCSS 8.4.31, và dòng 15 chưa có bản vá.

**Mức độ npm báo:** cao (high), gồm 4 lỗi:

| Lỗi | Mức | Nội dung |
|---|---|---|
| GHSA-6g55-p6wh-862q | Cao (CVSS 7.5) | Đọc trộm tệp qua chú thích `sourceMappingURL` trong CSS |
| GHSA-r28c-9q8g-f849 | Cao (CVSS 7.5) | Đọc trộm tệp `.map` qua đường dẫn `sourceMappingURL` |
| GHSA-qx2v-qp2m-jg93 | Trung bình (CVSS 6.1) | XSS khi CSS xuất ra có chuỗi `</style>` |
| GHSA-fxqj-rqcc-2cmp | Trung bình | Bản vá lỗi đầu tiên chưa kín |

**Rủi ro thực tế với shop: thấp.** Cả 4 lỗi chỉ xảy ra khi PostCSS xử lý CSS do kẻ xấu đưa vào. Ở đây PostCSS chỉ chạy lúc build trên máy mình và chỉ đọc CSS của shop (`app/globals.css`). Khách xem web không chạm được tới nó.

**Web tĩnh đang bán (`sport-shop-app`, thư mục `dist/`): không bị ảnh hưởng.** Bản này không dùng thư viện npm nào. CSS được `tools/build_storefront.py` (Python) chép thẳng vào trang, không qua PostCSS.

**Công sức nâng lên Next.js 16: nhỏ, khoảng 1 giờ.** Đã thử trên một bản sao, không đụng vào dự án:
- `next@16.4.6` (kèm PostCSS 8.5.23): `npm audit` báo 0 lỗi.
- `npm run build` thành công, không phải sửa mã. Next.js chỉ tự chỉnh `tsconfig.json` (`jsx` thành `react-jsx`, thêm `.next/dev/types/**/*.ts`).
- Ba bài kiểm thử trong `tests/` đều ra 0 lỗi.
- Chưa thử chế độ có backend (`API_URL`), vì backend chưa chạy được với PostgreSQL.

**Đã nâng cấp lên Next.js 16.4.6 (24/11/2026)** trên nhánh `dev`, đã gộp vào `main`, nhãn `ban-on-dinh-next16`:
- `npm audit`: 0 lỗi. Build không phải sửa mã (chỉ `tsconfig.json` tự chỉnh).
- Ba bài kiểm thử: 0 lỗi, chạy hai lượt.
- Bản trước khi nâng cấp (Next.js 15): nhãn `ban-on-dinh-2026-11-24`.

## Công cụ trên máy (kiểm tra ngày 24/11/2026)

| Công cụ | Tình trạng | Cần cho việc gì |
|---|---|---|
| Node.js | Có (v26) | Trang quản trị `sport-shop-app`, build Next.js |
| **Python** | **Đã cài 3.15.2 (24/11/2026)**, có pandas, openpyxl, pillow, playwright | **Bắt buộc cho việc cập nhật hằng ngày** |
| Java 21 + Maven | Chưa cài | Chỉ cho backend `sport-shop-next` (chưa dùng để bán) |
| Docker Desktop | Có cài nhưng bị treo, không chạy được | Chạy backend + PostgreSQL bằng `docker compose` |

**Python là bắt buộc.** Nút `cap-nhat-web.bat` chạy `python tools\daily_update.py`: đọc file Excel Sapo, nhập vào trang quản trị, rồi xuất web tĩnh. Không có Python thì **không cập nhật được hàng và tồn kho lên web**.

Cài Python:
1. Tải Python 3.12 trở lên từ python.org. Khi cài, **đánh dấu ô "Add python.exe to PATH"**.
2. Mở cửa sổ lệnh mới, chạy: `pip install pandas openpyxl pillow`
3. Muốn chạy kiểm thử thì cài thêm: `pip install playwright` rồi `playwright install chromium`

Đã kiểm tra với Python vừa cài (24/11/2026):
- `python tools\daily_update.py --export-only` chạy được, xuất `dist/` đủ 175 sản phẩm, 953 phiên bản.
- Đọc file Sapo thật ngày 14/11/2026 (pandas 3.1.1): đúng mốc 175 sản phẩm, 953 phiên bản, bỏ 68 phiên bản giá 0. Kết quả giống hệt `data/seed-products.json`.
- **Còn thiếu cho nút cập nhật đầy đủ:** tệp `sport-shop-app/.env` có `ADMIN_PASSWORD` (chép từ `.env.example`). Thiếu tệp này thì bước nhập Excel dừng với báo "Thiếu ADMIN_PASSWORD"; riêng `--export-only` vẫn chạy.

Ghi chú: Java và Maven lúc kiểm thử backend là bản di động trong thư mục tạm, không cài vào máy. Chromium của Playwright nằm ở `C:\Users\Admin\AppData\Local\ms-playwright`.
