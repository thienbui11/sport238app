# Cập nhật hàng lên web mỗi ngày

Dành cho chủ shop. Chỉ cần 2 bước, mất khoảng 1 phút.

## Mỗi ngày

1. Trong **Sapo**, vào Sản phẩm → **Xuất file** → chọn *Tất cả sản phẩm* → tải về.
   File tự nằm trong thư mục **Tải về** (Downloads), tên kiểu `danh_sach_san_pham_24.11.2026_….xlsx`.
2. Bấm đúp **`cap-nhat-web.bat`** (trong thư mục `sport-shop-app`).

Công cụ sẽ tự làm:

| Bước | Việc | Ghi chú |
|---|---|---|
| 1 | Lấy file Sapo **mới nhất** trong Tải về | Chỉ **chép** sang `inbox`, file gốc trong Tải về giữ nguyên |
| 2 | Kiểm tra file | Thiếu cột, file hỏng → **dừng, không nhập** (file được để sang `inbox\loi`) |
| 3 | So với hàng đang có trên web | Số sản phẩm hoặc số size/màu **giảm hơn 30%** (thường do xuất nhầm khi đang lọc trong Sapo) → **dừng và hỏi** |
| 4 | Sao lưu dữ liệu | Vào `data\sao-luu\`, giữ 30 lần gần nhất |
| 5 | Nhập vào trang quản trị | Ảnh, tên hiển thị, mô tả, danh mục chọn tay **giữ nguyên** |
| 6 | Mở **báo cáo thay đổi** | Sản phẩm mới, sản phẩm không còn trong file (tự ẩn), đổi giá, vừa hết hàng, có hàng lại |
| 7 | Xuất web vào thư mục `dist` | Rồi đưa lên mạng (xem `HUONG-DAN-DUA-LEN-MANG.md`) |

Trang quản trị chưa mở thì công cụ tự mở tạm rồi tự tắt khi xong.
Hôm nào không có file mới thì công cụ chỉ xuất lại web (để ảnh, mô tả vừa sửa lên mạng).

## Khi công cụ dừng lại

- **"FILE KHÔNG DÙNG ĐƯỢC"**: file không phải "Danh sách sản phẩm" của Sapo, hoặc tải chưa xong. Xuất lại từ Sapo rồi bấm lại.
- **"DỪNG, CHƯA NHẬP: Số sản phẩm giảm mạnh"**: kiểm tra trong Sapo có đang lọc theo loại, kho, nhãn hiệu không; bỏ lọc, xuất lại.
  Nếu anh/chị chắc chắn file đúng (ví dụ vừa xóa nhiều mẫu cũ trong Sapo): bấm lại `cap-nhat-web.bat`, khi được hỏi thì gõ `c` rồi Enter.

Nhật ký mọi lần chạy: `daily_update.log`. Báo cáo thay đổi: thư mục `bao-cao`.

## Lỡ nhập nhầm: quay lại dữ liệu cũ

1. Đóng cửa sổ trang quản trị (`chay-quan-tri.bat`) nếu đang mở.
2. Bấm đúp **`khoi-phuc.bat`** → chọn số của lần muốn quay lại (mới nhất ở trên) → gõ `c` để đồng ý.
3. Mở lại trang quản trị, kiểm tra, rồi bấm `cap-nhat-web.bat` để xuất lại web.

Dữ liệu ngay trước khi khôi phục cũng được sao lưu (tên có chữ `truoc-khoi-phuc`), nên khôi phục nhầm vẫn quay lại được.

## Cho máy tự cập nhật mỗi tối (không bắt buộc)

Bấm chuột phải vào **`dat-lich.ps1`** → *Run with PowerShell*. Mặc định máy tự chạy lúc **21:15** mỗi ngày (sau giờ đóng cửa).
Đổi giờ: mở PowerShell trong thư mục này, gõ `.\dat-lich.ps1 -Gio 20:30`. Gỡ lịch: `.\dat-lich.ps1 -Go`.

- Máy phải đang bật (không ngủ) lúc đó, và anh/chị vẫn phải bấm **Xuất file** trong Sapo trước giờ đó (Sapo chưa cho tự lấy dữ liệu, xem dưới).
- Chạy theo lịch thì không hỏi gì: file bất thường là **dừng, không nhập**, ghi lý do vào `daily_update.log`.

## Cài đặt (tệp `.env`, không đưa lên mạng)

| Dòng | Ý nghĩa | Mặc định |
|---|---|---|
| `ADMIN_PASSWORD=` | Mật khẩu trang quản trị (bắt buộc) | — |
| `TAI_VE=` | Thư mục Tải về để tự lấy file Sapo; `TAI_VE=khong` để tắt | Downloads của máy |
| `INBOX=` | Thư mục bỏ file Excel bằng tay | `inbox` |
| `XUAT_WEB=html` | Luôn xuất bằng bản HTML dự phòng | Next.js, lỗi thì HTML |
| `DEPLOY_CMD=` | Lệnh đưa web lên mạng sau khi xuất | không đưa |

## Tự lấy dữ liệu từ Sapo (chưa làm được, ghi lại để sau)

Tìm hiểu ngày 24/11/2026:

- Sapo có **"Ứng dụng riêng" (Private App)**: vào Ứng dụng → Ứng dụng riêng → Tạo ứng dụng riêng, cấp quyền *Chỉ đọc* cho "Sản phẩm, phiên bản và danh mục", hệ thống cấp **API key + API secret**; gọi API bằng Basic Authentication. Trang hướng dẫn của Sapo ghi đây là công cụ **trên Sapo Web**, không nói tới Sapo POS/Omni. ([support.sapo.vn – Ứng dụng riêng](https://support.sapo.vn/ung-dung-rieng-private-apps))
- Một bên tích hợp (Casso) ghi: *"chưa hỗ trợ với Sapo Omni vì Sapo có thu phí API Omni theo tháng"* – tức API cho bản bán tại quầy có thể **tốn phí**. ([flow.casso.vn – Tích hợp Sapo](https://flow.casso.vn/tich-hop/sapo/))
- Có dự án mã nguồn mở dùng cùng cách (API key, secret, địa chỉ `…mysapo.net`) cho Sapo Omni, gồm đọc sản phẩm và tồn kho. ([GitHub – sapo-omni-mcp](https://github.com/minhquy3101/sapo-omni-mcp/blob/main/README.md))

**Việc anh/chị cần hỏi Sapo** (không tự đăng ký): gói Sapo của shop có tạo được "Ứng dụng riêng" không, có mất phí không, quyền đọc tồn kho theo chi nhánh.
Khi có API key (quyền *Chỉ đọc*), chỉ cần thay bước 1 ở trên (đọc Excel) bằng gọi API; các bước kiểm tra, sao lưu, báo cáo giữ nguyên.
Công cụ **không** dùng mật khẩu đăng nhập Sapo của anh/chị, và vẫn chỉ đọc giá bán lẻ và tồn kho (không đọc giá nhập, giá vốn).
