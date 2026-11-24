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
