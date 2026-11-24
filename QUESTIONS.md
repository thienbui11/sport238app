# QUESTIONS – Việc cần chủ shop quyết định hoặc cung cấp

Ở chế độ tự chủ, gặp chỗ cần anh/chị quyết định thì tôi **tạm chọn phương án an toàn, dễ đổi lại** và làm tiếp. Anh/chị chỉ cần trả lời theo mã câu.

| Mã | Câu hỏi | Các lựa chọn | Đang tạm dùng | Ảnh hưởng nếu đổi |
|---|---|---|---|---|
| Q1 ✅ ĐÃ DUYỆT (E2, 24/11) | Hợp nhất về **một bản giao diện**? | (a) Next.js xuất web tĩnh làm bản chính, bản HTML giữ làm dự phòng; (b) giữ HTML, bỏ React; (c) giữ cả hai | **(a)**, chuẩn bị trên nhánh riêng, chứng minh bằng kiểm thử. **Chưa xóa** bản nào. Xóa hẳn bản HTML cần anh/chị đồng ý | Nếu chọn (b) hoặc (c): các chức năng mới phải làm lại cho bản HTML |
| Q2 | Số 0962 374 770 có nhận **cuộc gọi thường** không? | Có / Không / số khác | Nút "Gọi điện" đã làm sẵn nhưng **ẩn** cho tới khi có số gọi được (nhập trong trang quản trị, mục Cài đặt) | Có số là nút hiện ngay |
| Q3 | **Bảng size giày**, và bảng của CV, HD Sport, Wika, Mira, Peace Max | Gửi ảnh hoặc số liệu | Ghi "Chưa có bảng size, nhắn shop để được tư vấn" | Có số liệu là thêm được ngay |
| Q4 | Hai bảng size **không ghi tên hãng** (nền vàng "S < 165 cm"; nền trắng "1m50–1m55") là của hãng nào? | Tên hãng | **Không hiện** lên web (tránh khách đọc nhầm bảng) | Có tên hãng là bật lên |
| Q5 ✅ KHÔNG đưa lên web (24/11) | **Thẻ tích điểm** (mỗi 100k một ô; 5 ô: túi rút hoặc 2 cuộn keo; 10 ô: bó gối/gót; 15 ô: túi 2 ngăn; 20 ô: bộ áo CLB/đội tuyển) có ghi lên web không? Có áp dụng cho khách đặt qua web không? | Có / Không | Không ghi (chưa rõ điều kiện) | Có thể thêm một khối nhỏ ở trang chủ |
| Q6 | Đặt đồng phục đội: giá in tên số, số lượng tối thiểu, thời gian làm, có in logo không? | Số liệu | Chức năng tạo tin nhắn đặt đội đã làm; các mục giá in, thời gian ghi "shop báo giá" | Có số liệu là hiện tạm tính đầy đủ |
| Q7 | Mật khẩu quản trị: tạo tệp `sport-shop-app/.env` với `ADMIN_PASSWORD` mạnh | Anh/chị tự đặt | Chưa có tệp; mật khẩu mặc định `admin123` chỉ dùng trên máy shop | Thiếu tệp thì nút cập nhật không nhập được Excel |
| Q8 | Thư mục ảnh sản phẩm (ví dụ `D:\anh-san-pham`) | Đường dẫn | Công cụ nạp ảnh đã sẵn, chạy được với mọi thư mục | – |
| Q9 | Tên miền riêng (nếu muốn) và tài khoản Cloudflare | Anh/chị tự đăng ký | Đã chuẩn bị hướng dẫn và lệnh; chưa đưa lên mạng | – |
