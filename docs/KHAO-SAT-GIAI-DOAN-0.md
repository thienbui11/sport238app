# Khảo sát Giai đoạn 0 – web SPORT 238 (24/11/2026)

Phạm vi: bản đang bán là web tĩnh `sport-shop-app/dist`, cùng trang quản trị. Chỉ khảo sát, **không sửa mã**. Không cài đặt, không build, không chạy lại ba bài kiểm thử, không chạy backend Spring Boot.
Cách làm: đọc mã nguồn, mở web bằng Chromium thật qua Playwright trên máy tính (1366 px) và điện thoại (390 px), ở cả chế độ sáng lẫn tối, rồi đo tự động.

Ảnh chụp hiện trạng (32 ảnh, nén JPEG): `docs/anh-hien-trang/24-11-2026-truoc/`.
Tên ảnh có dạng `số-nội dung-thiết bị-chế độ`, với `pc` là máy tính, `dt` là điện thoại.

## 1. Tóm tắt

- Web chạy ổn định: không có lỗi JavaScript, không bị tràn ngang ở 390 px, chế độ tối hiển thị đúng, không lộ giá nhập hay giá vốn.
- **Vấn đề lớn nhất là trên điện thoại**, trong khi phần lớn khách vào từ Zalo/Facebook bằng điện thoại:
  - Mỗi hàng chỉ có 1 sản phẩm, mỗi thẻ cao 623 px.
  - Cả trang cao **119.543 px**, khoảng 140 lần màn hình.
  - Sản phẩm đầu tiên nằm cách đầu trang 3.908 px (khoảng 4,6 màn hình).
  - Mục "Về shop" và "Cách mua" nằm ở khoảng 117.600 px, gần như không ai kéo tới.
  - Trên điện thoại cũng không có menu để nhảy nhanh tới các mục này.
- **Tìm kiếm phải gõ đúng dấu**: "giay" ra 0 kết quả, "giày" ra 36.
- **Xem chi tiết xong bấm quay lại thì mất chỗ đang xem**: đang ở sản phẩm thứ 31 (vị trí 23.049 px) thì bị đưa về đầu danh sách (3.275 px).
- Nội dung còn trống: 0/175 sản phẩm có ảnh thật, 0/175 có mô tả. Mọi thẻ chỉ có hình emoji giống nhau.

## 2. Chức năng hiện có

| Khu vực | Có gì | Nhận xét |
|---|---|---|
| Trang chủ | Phần mở đầu, 4 ô số liệu, dải chữ chạy, 8 ô danh mục, dải "Hàng đang có sẵn" (10 món), banner đồng phục, Về shop, Cách mua | Trên máy tính đẹp. Trên điện thoại quá dài (xem mục 3) |
| Danh sách sản phẩm | Ô tìm kiếm, lọc theo tình trạng, sắp xếp theo giá, 8 nút danh mục, chọn màu/size và thêm giỏ ngay trên thẻ | Hiện cùng lúc cả 175 sản phẩm, không chia trang |
| Trang chi tiết | Ảnh (chưa có ảnh thật), chọn màu/loại, size chia nhóm người lớn/trẻ em, số tồn từng size, mã sản phẩm, nút hỏi shop, địa chỉ nhận hàng | Tốt. Còn một số lỗi nhỏ (mục 3) |
| Giỏ hàng | Tăng/giảm số lượng, tạm tính, nội dung đơn hàng có mã từng món, sao chép đơn rồi mở Zalo/Messenger, có cách sao chép dự phòng | Rõ ràng, đúng quy tắc "ghé shop nhận hàng" |
| Chặn quá tồn | Không cho thêm vượt số tồn | **Vẫn chờ chủ shop quyết định có giữ hay không** (CLAUDE.md, mục 3) |
| Trang quản trị | Đăng nhập (khóa sau 5 lần sai), danh sách sản phẩm, lọc chưa có ảnh/đang ẩn/nổi bật, sửa tên hiển thị, mô tả, danh mục, ẩn, nổi bật, ảnh theo màu (tự thu nhỏ), nhập JSON, cài đặt shop | Nút đăng xuất không hoạt động (mục 5) |
| Cập nhật hằng ngày | `cap-nhat-web.bat`: Excel mới nhất trong `inbox/` → nhập vào quản trị → xuất `dist/` | Chưa có tệp `.env` nên chưa nhập được Excel (PROGRESS.md đã ghi) |

## 3. Lỗi trải nghiệm của khách (sắp theo mức ảnh hưởng)

### Ưu tiên cao
1. **Điện thoại: 1 sản phẩm mỗi hàng, trang dài 119.543 px.** Lưới đặt chiều rộng tối thiểu 230 px nên màn 390 px chỉ chứa được 1 cột. Phần mở đầu và hình trang trí chiếm khoảng 1,5 màn hình trước khi tới danh mục. Ảnh: `01-trangchu-dt-light.png`, `07-luoi-sanpham-dt.png`.
2. **Điện thoại và máy tính bảng (dưới 1000 px) không có menu.** Thanh menu bị ẩn mà không có nút ☰ thay thế. Khách không có cách nào nhảy tới "Cách mua" hay "Về shop".
3. **Tìm kiếm không hiểu chữ không dấu**, cũng không tìm được theo mã sản phẩm (PVN…) hay theo hãng.
4. **Quay lại thì mất chỗ đang xem.** Cả nút Back của trình duyệt lẫn nút "← Tất cả sản phẩm" đều đưa về đầu danh sách.
5. **Nút Zalo nổi che nút bấm.** Trên điện thoại, nút tròn ở góc dưới đè lên nút "+ Thêm vào giỏ", nút size và nút màu trên thẻ. Ở trang chi tiết, nó che nút chọn loại "Fire". Ảnh: `04-chitiet-nhieumau-dt-light.png`.

### Ưu tiên vừa
6. **Lựa chọn màu trên thẻ không được mang sang trang chi tiết.** Ví dụ: chọn "Vàng" trên thẻ, sang trang chi tiết lại hiện "Xanh cổ vịt". Trang chi tiết luôn chọn sẵn màu đầu tiên, kể cả khi màu đó đã hết hàng.
7. **Nút size/màu trên thẻ nhỏ**, cao khoảng 24 px, dễ bấm nhầm bằng ngón tay (nên khoảng 40–44 px).
8. **Thông báo nhanh che nút.** Dòng "Bạn chưa chọn size…" che giá và nút thêm giỏ (`09-chua-chon-size-dt.png`). Trong giỏ, dòng "Đã thêm vào giỏ hàng" che nút Messenger (`05-giohang-dt-light.png`).
9. **"Xóa giỏ hàng" xóa ngay**, không hỏi lại và không hoàn tác được. Bấm "−" khi số lượng là 1 cũng xóa món đó luôn.
10. **"Hỏi shop về sản phẩm này" mở Messenger trống trơn.** Khách phải tự gõ lại tên sản phẩm. Nên sao chép sẵn "Mình hỏi về [tên] – mã [PVN…]" giống như giỏ hàng.
11. **Gửi link sản phẩm qua Zalo/Facebook không hiện đúng sản phẩm.** Link sản phẩm có dạng `/#p-PVN…`, nên khi chia sẻ chỉ hiện tiêu đề chung của shop. Google cũng không đọc được từng sản phẩm, vì nội dung chỉ được tạo bằng JavaScript.
12. **Dải "MỚI CẬP NHẬT – Hàng đang có sẵn" không thật sự là hàng mới.** Đây chỉ là 10 món còn hàng đầu tiên theo thứ tự trong Sapo.

### Bàn phím và trình đọc màn hình
13. **Khi giỏ hàng đang đóng, phím Tab vẫn đi qua 4 nút vô hình trong giỏ** (Đóng, Zalo, Messenger, Xóa giỏ hàng).
14. **Mở giỏ hàng xong, vị trí con trỏ vẫn ở nút giỏ** chứ không chuyển vào trong giỏ, và Tab có thể đi ra ngoài giỏ. Giỏ cũng chưa được khai báo là hộp thoại.
15. **Một số nhãn chưa đủ thông tin cho trình đọc màn hình:**
    - Nút giỏ không đọc số món đang có.
    - Nút "Giảm"/"Tăng" không nói là của món nào.
    - Đổi bộ lọc xong không đọc số kết quả.
    - Nút size ở trang chi tiết bị đọc dính chữ, ví dụ "39còn 1".

## 4. Đánh giá giao diện

**Đã tốt (nên giữ):**
- Màu đỏ đô và đen đúng logo, dùng nhất quán.
- Phần mở đầu trên máy tính mạnh và rõ.
- Chữ tiếng Việt dễ đọc (font Be Vietnam Pro).
- Chế độ tối đồng bộ, có tôn trọng cài đặt "giảm chuyển động" của máy.
- Nội dung đơn hàng rõ, có mã từng món.
- Chữ "ghé shop nhận hàng" lặp lại ở nhiều chỗ.

**Nên cải thiện:**
- **Ảnh sản phẩm** là điểm yếu lớn nhất. Cả 175 thẻ là emoji 👕 hoặc 👟 trên nền màu, cùng danh mục thì trông y hệt nhau. Trong chế độ tối, nền màu nhạt này còn bị chói.
- Trên điện thoại, phần mở đầu quá cao. Ô tìm kiếm và hai ô chọn xếp thành 3 dòng, chiếm khoảng 350 px.
- Danh mục "Giày bóng đá" đang chứa cả giày vải, giày thể thao, giày trẻ em (ví dụ "Giày vải – Đế bằng", "Giày thể thao CP-005"). Khách tìm giày thường sẽ không nghĩ tới mục này.
- Còn thiếu hẳn một số thông tin: **giờ mở cửa** (quan trọng vì khách phải ghé shop), bản đồ hoặc nút chỉ đường gần đầu trang, **bảng size**.
- 44/175 sản phẩm (25%) đang hết hàng nhưng vẫn hiện trong danh sách (xếp cuối).

## 5. Nợ kỹ thuật

| # | Vấn đề | Mức |
|---|---|---|
| 1 | Hai bản giao diện (HTML thuần và React) phải sửa tay cho giống nhau, không có công cụ kiểm tra tự động. Mã JavaScript trong `storefront.template.html` bị viết dồn, có dòng dài hơn 1000 ký tự, khó sửa | Cao |
| 2 | `globals.css` được vá chồng nhiều lớp: cùng một quy tắc khai báo lại ở nhiều chỗ (`.art .e1/.e2/.e3`, `.opt`, `.sz`, ẩn `.menu` hai lần). Còn CSS thừa không dùng (`.pal`, `.art .e4`, `.sz u`, `.df small`) và hàm rỗng `bindAdd()` | Vừa |
| 3 | `index.html` nặng 126 KB, trong đó 78 KB là logo nhúng 3 lần. Riêng logo 200 px chiếm 55 KB. `logo.png` nặng 118 KB | Vừa |
| 4 | Trang tải cấu hình xong mới tải sản phẩm (hai lượt chờ nối tiếp). Font Google chưa có `preconnect` | Thấp |
| 5 | `products.json` công khai chứa cả trường nội bộ không cần (`active`, `hidden`, `category_auto`, `category_override`, `product_type`). **Không có giá nhập hay giá vốn**: đã kiểm tra, mỗi phiên bản chỉ có `id, sku, option1, option2, price, inventory_quantity` | Thấp |
| 6 | **Trang quản trị: "Đăng xuất" không hoạt động.** Cookie đăng nhập đặt kiểu HttpOnly nên JavaScript không xóa được. Đã thử: bấm đăng xuất, tải lại trang vẫn đang đăng nhập | Vừa |
| 7 | Trang quản trị cho chọn tệp `.xlsx`, nhưng máy chủ Node chỉ nhận JSON, nên chỉ báo chung chung "File không hợp lệ". Phiên đăng nhập và bộ đếm sai mật khẩu nằm trong bộ nhớ, không bao giờ được dọn | Thấp |
| 8 | Địa chỉ web lỗi mã hóa (ví dụ `/%E0`) làm máy chủ trả lỗi 500 và ghi log lỗi | Thấp |
| 9 | Tài liệu lệch nhau: `sport-shop-next/README.md` ghi 932 phiên bản, CLAUDE.md và PROGRESS.md ghi 953 | Thấp |

**Rút lại một nhận định:** lúc đầu tôi tưởng `cap-nhat-web.bat` hỏng vì lệnh `python` trỏ vào lối tắt Microsoft Store. Kiểm tra lại PATH trong registry thì Python 3.15 đã đứng trước, nên bấm đúp tệp `.bat` vẫn chạy đúng. Chỉ những cửa sổ mở từ trước khi cài Python, như VS Code đang mở, mới còn giữ PATH cũ. Muốn chạy lệnh `python` trong VS Code thì khởi động lại VS Code.

## 6. Câu hỏi cho chủ shop

1. Giờ mở cửa của shop là mấy giờ, các ngày nào? (để ghi lên web)
2. Có giữ việc **chặn đặt quá số tồn** trong giỏ không?
3. Ảnh sản phẩm đang lưu ở đâu: thư mục trên máy, điện thoại, hay trên Facebook?
4. Có muốn tách "Giày bóng đá" thành "Giày" (gồm giày đá bóng, giày thể thao, giày vải), hay giữ đúng 8 danh mục và chỉnh tay từng sản phẩm?
5. Có bảng size (áo người lớn, áo trẻ em, giày) để đưa lên web không?

## 7. Đề xuất thứ tự cho giai đoạn sau (chỉ đề xuất, chưa làm)

1. Điện thoại: lưới 2 cột với thẻ gọn hơn, nút "Xem thêm" (khoảng 20 món mỗi lần), phần mở đầu thấp hơn, thêm menu ☰. *(lỗi 1, 2)*
2. Tìm kiếm không cần dấu, tìm được theo mã và hãng. *(lỗi 3)*
3. Giữ vị trí khi quay lại; nút Zalo nổi không che nút bấm; mang lựa chọn màu sang trang chi tiết. *(lỗi 4, 5, 6)*
4. Nút size/màu to hơn, sửa thông báo che nút, hỏi lại trước khi xóa giỏ, nút "Hỏi shop" sao chép sẵn tên sản phẩm. *(lỗi 7–10)*
5. Sửa phần bàn phím và trình đọc màn hình. *(lỗi 13–15)*
6. Thêm giờ mở cửa, nút chỉ đường, bảng size (cần chủ shop cung cấp thông tin).
7. Mỗi sản phẩm có trang tĩnh riêng khi xuất web, để gửi link Zalo/Facebook hiện đúng tên và ảnh sản phẩm. *(lỗi 11)*
8. Dọn nợ kỹ thuật 2–4 và sửa nút đăng xuất của trang quản trị.

Mọi thay đổi giao diện phải sửa ở cả hai bản: mẫu HTML và React, CSS dùng chung. Sau đó chạy ba bài kiểm thử trên máy tính và điện thoại.
