# Kiểm thử cửa hàng bằng trình duyệt thật (Playwright)

Cài một lần:  `pip install playwright` rồi `playwright install chromium`

Chạy (trang quản trị phải đang chạy với dữ liệu mẫu sạch: xóa `sport-shop-app/data/shop.db*` rồi `npm start`):

    python tests/test_all.py   http://localhost:3000   # 175 trang chi tiết, 8 danh mục, link Facebook/Zalo, giỏ hàng, điện thoại
    python tests/test_feat.py  http://localhost:3000   # chọn size, thêm giỏ, sao chép đơn, mở Zalo, mở Messenger, dự phòng clipboard
    python tests/test_cards.py http://localhost:3000   # chọn màu/size trên thẻ, tồn kho, cảnh báo vượt tồn, hết hàng
    python tests/test_mobile.py http://localhost:3000  # điện thoại 2 cột, menu, tìm không dấu, quay lại đúng chỗ, nút ≥ 44 px, xóa giỏ, đăng xuất

Chạy trên web tĩnh: `python sport-shop-app/tools/export_static.py`, rồi `python -m http.server 8099 --directory sport-shop-app/dist`
và chạy ba lệnh trên với `http://localhost:8099`.

Các bài kiểm thử dựa vào dữ liệu mẫu (175 sản phẩm). Ảnh chụp màn hình ra thư mục `tests/out/`.
Mỗi bài in "KẾT QUẢ: 0 lỗi" khi đạt.

## pytest (công cụ Python)

    py -m pytest          # chạy mọi bài trong tests/py (pytest.ini đã chỉ đúng thư mục)

Mỗi bài tự bật máy chủ quản trị Node riêng với dữ liệu mẫu trong thư mục tạm (không đụng dữ liệu thật).
- `tests/py/test_nap_anh.py`: nạp ảnh hàng loạt theo mã SKU (đúng SP/màu, WebP ≤ 1400 px, xoay đúng chiều, giữ ảnh cũ, không nạp trùng, báo cáo).
- `tests/py/test_sapo_parser.py`: bộ đọc Excel Python (9 danh mục, tách size, file thật 14/11: 175 SP, 953 phiên bản, 632 SP trong file, bỏ 68 phiên bản giá 0, không có giá nhập; dữ liệu mẫu = kết quả bộ đọc).
- `tests/py/test_server.py`: máy chủ Node (đường dẫn lỗi mã hóa → 400; chọn file Excel ở trang quản trị → báo rõ cách nhập).

## Đối chiếu bộ đọc Python với Java (khi sửa quy tắc phân loại)
Cần JDK 21 và Maven (bản zip di động trong thư mục tạm là đủ; đặt JAVA_HOME và PATH trong phiên lệnh):

    py sport-shop-app/tools/sapo_xlsx_to_json.py <file.xlsx> py.json
    cd sport-shop-next/backend
    SAPO_XLSX=<file.xlsx> PY_JSON=<đường dẫn py.json> mvn -B test     # ParityWithPythonTest in "Python = Java: 175 sản phẩm…"

## Web tĩnh bản Next.js (bản chính) + kiểm tra SEO

    py sport-shop-app/tools/export_next.py --server http://localhost:3000 --out <thư mục tạm> --site-url https://vidu.vn --updated 24/11/2026
    py -m http.server 3602 --directory <thư mục tạm>       # rồi chạy 4 bài Playwright với http://localhost:3602
    py tests/test_seo.py <thư mục tạm> https://vidu.vn     # title/description/og/canonical/JSON-LD từng trang, sitemap, robots, không có admin, không lộ giá nhập

`export_next.py` xóa và build lại `sport-shop-next/frontend/.next`: **tắt máy chủ `next start` trước** (và kiểm tra cổng 3100 đã trống: tắt tác vụ nền chưa chắc tắt tiến trình node con).
- `tests/py/test_xuat_web.py`: nút cập nhật xuất bằng Next.js; lỗi thì tự dùng bản HTML; `XUAT_WEB=html` luôn dùng HTML.
