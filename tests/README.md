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
- `tests/py/test_nhap_an_toan.py`: nhập hằng ngày an toàn (chép từ Tải về không xóa gốc, thiếu cột → dừng, số SP/phiên bản giảm > 30% → dừng trừ khi xác nhận, sao lưu/khôi phục, báo cáo thay đổi, tự bật trang quản trị; cả quy trình với bản chép file Excel thật 14/11).
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

## Truy cập (axe) và Lighthouse
Cài một lần: `cd tests && npm install` (axe-core 4.14.0, lighthouse 13.6.0; tests/node_modules không commit).

    py tests/test_a11y.py http://localhost:3602     # axe: 5 màn hình × máy tính/điện thoại × sáng/tối; đạt khi 0 lỗi critical/serious
    py tests/lighthouse.py http://localhost:3602    # điện thoại giả lập; trang chủ + 1 trang SP; đạt khi cả 4 mục ≥ 90; báo cáo tests/out/lighthouse/

## Trang quản trị (B6 + N2)

    py tests/test_admin.py     # tự bật máy chủ Node riêng với dữ liệu mẫu trong thư mục tạm (không cần máy chủ đang chạy)

Kiểm tra: hai bản sao admin giống hệt; số trên các nút lọc (Chưa có ảnh, Hết hàng, Chưa có mô tả, Đang ẩn, Nổi bật) đúng với API; sắp xếp theo tồn;
sửa hàng loạt Ẩn/Hiện, Bật/Tắt nổi bật, Đổi danh mục/Tự động (đối chiếu `/api/admin/products`, giữ nguyên tên riêng, mô tả, danh mục đặt tay);
sửa 1 SP + tải ảnh (đổi WebP ≤ 1400 px); điện thoại 390/320 px sáng/tối (thẻ không bị cắt, nút ≥ 40 px, thanh sửa hàng loạt ở đáy); axe; đăng xuất.

## Giao diện mới (D1–D4) và ảnh chụp (D7)

    py tests/test_giao_dien.py http://localhost:3602     # chống tái phát giao diện mới (chỉ bản Next.js; bản HTML dự phòng vẫn dùng emoji); in "KẾT QUẢ: 0 lỗi"
    py tests/chup_anh.py http://localhost:3602 screenshots/after   # chụp 17 màn hình chính (JPG nén), so sánh ở screenshots/so-sanh.html

`test_giao_dien.py` kiểm tra: không emoji trang trí (ô danh mục, ô giữ chỗ ảnh, nút, thanh trên/dưới, CSS), biểu tượng là SVG;
thanh "Thêm vào giỏ" dính đáy màn hình ở trang chi tiết trên điện thoại (thay thanh dưới, không che nút/link nào, bấm được, chân trang không bị che);
không tràn ngang ở 320/390/768/1366 px; không chuyển động lặp vô hạn, không backdrop-filter, tôn trọng "giảm chuyển động";
tương phản chữ các thành phần mới ở sáng/tối; khung ảnh vuông, ảnh có width/height, CLS < 0,05; nút tìm nhanh ở đầu trang.
Ô giữ chỗ ảnh tô theo màu sản phẩm (ví dụ áo "… Đỏ" ra màu đỏ).

## Bảng size và gợi ý size (chỉ bản Next.js)

    py tests/test_bang_size.py http://localhost:3602   # 15 bảng khớp từng ô với data/bang-size.json; gợi ý size đúng như tra tay; nút Bảng size ở trang SP; axe; sáng/tối
    py tests/test_trang_sp.py http://localhost:3602    # hỏi shop (sao chép câu hỏi), chia sẻ, bản đồ tải khi bấm, SP cùng loại, đã xem gần đây
    py tests/test_loc.py http://localhost:3602         # lọc size còn hàng, giá, hãng (so với products.json), Yêu thích (lưu trên máy)
    py tests/test_dat_doi.py http://localhost:3602     # đặt đồng phục đội: tiền áo, giá in (dưới 5 bộ báo giá, từ 5 bộ 15k, từ 10 bộ 10k), danh sách in, tin nhắn Zalo
    py tests/test_pwa_anh.py http://localhost:3602     # cài như ứng dụng (manifest, biểu tượng, favicon) + gửi đơn kèm ảnh (chia sẻ của điện thoại)
