# BACKLOG – SPORT 238

Xếp theo lợi ích ÷ công sức (cao trước). Độ khó: S < nửa ngày, M 1–2 ngày, L ≥ 3 ngày. Trạng thái: ⬜ chưa làm · 🔄 đang làm · ✅ xong.
"Xong khi…" luôn gồm tiêu chuẩn chung: kiểm thử Playwright đạt ở máy tính và điện thoại 390 px, sáng và tối; không lỗi console, không tràn ngang; axe 0 lỗi nghiêm trọng; không lộ giá nhập; chữ tiếng Việt đúng.

## Đợt 1 – nền tảng (chạy song song, mỗi việc một nhánh)
| Mã | Việc | Lợi ích | Độ khó | Xong khi… | TT |
|---|---|---|---|---|---|
| K1 | Khảo sát sâu: trang quản trị, cập nhật hằng ngày, xuất web tĩnh, bảo mật | Biết hết lỗi còn lại | M | AUDIT.md có mục quản trị, vận hành, bảo mật; ảnh trang quản trị trong `screenshots/before/` | 🔄 |
| K2 | Tìm ý tưởng từ các shop thể thao, trang bán hàng tốt | Chọn đúng việc đáng làm | S | Có danh sách ý tưởng kèm nguồn, đã đưa vào backlog | 🔄 |
| P1 | Danh mục "Giày thể thao" (Python + Java), pytest cho bộ đọc Excel, đối chiếu Python–Java trên file thật | Khách tìm giày đúng chỗ; nhập hàng an toàn | M | pytest đạt; Python = Java trên file 14/11 (175 SP, 953 phiên bản, 632 dòng, bỏ 68); 9 danh mục ở cả hai giao diện và trang quản trị | 🔄 |
| F1 | Nạp ảnh hàng loạt theo mã SKU (thu nhỏ, WebP, theo màu, báo cáo HTML) | Có ảnh thật nhanh | M | Lệnh chạy với thư mục mẫu: ảnh đúng SP/màu, giữ ảnh cũ, báo tệp sai mã, báo SP thiếu ảnh; có kiểm thử | 🔄 |
| F2 | Trang quản trị: lọc hết hàng / chưa mô tả / chưa ảnh, sửa hàng loạt (ẩn, nổi bật, danh mục), ảnh tải lên đổi WebP | Chủ shop đỡ tốn thời gian | M | Playwright cho từng thao tác; hai bản sao admin giống nhau | 🔄 |
| G1 | Nhập hàng mỗi ngày: nhận file mới trong Tải về (chép, không xóa), kiểm tra file (thiếu cột, số SP giảm bất thường → dừng), sao lưu trước khi nhập, quay lại bản trước, báo cáo thay đổi HTML, một nút làm hết, hướng dẫn Task Scheduler, tìm hiểu API Sapo | Cập nhật hằng ngày an toàn, ít thao tác | M–L | pytest cho kiểm tra file, báo cáo, sao lưu/khôi phục; chạy thật với file 14/11 trên dữ liệu thử | 🔄 |
| H1 | Next.js xuất web tĩnh: mỗi SP một trang (tiêu đề, mô tả, Open Graph, dữ liệu cấu trúc), sitemap, robots, tự chép ảnh, font chạy không cần mạng; không đưa trang quản trị ra ngoài | Một bản giao diện; Google và Zalo thấy từng SP | M–L | 4 bài kiểm thử cũ đạt trên thư mục xuất; có kiểm thử trang SP, meta, sitemap | 🔄 |
| S1 | Chép bảng size từ ảnh chủ shop gửi (2 người chép độc lập, đối chiếu) | Dữ liệu cho bảng size, gợi ý size | S | Tệp dữ liệu bảng size khớp ảnh 100%; hãng thiếu ghi rõ | 🔄 |
| T1 | Kiểm thử axe + Lighthouse tự động, GitHub Actions (chưa push) | Giữ chất lượng lâu dài | M | Lệnh chạy được trên máy; có số liệu nền; tệp CI sẵn sàng | 🔄 |
| J1 | Hướng dẫn đưa lên mạng miễn phí (điều khoản hiện hành, Cloudflare Pages, tên miền, HTTPS, thống kê) | Chủ shop tự đưa lên được | S–M | HUONG-DAN-DUA-LEN-MANG.md viết lại, có nguồn, lệnh đưa lên tự động | 🔄 |

## Đợt 2 – giao diện và chức năng cho khách (trên bản chính sau khi hợp nhất)
| Mã | Việc | Lợi ích | Độ khó | Xong khi… | TT |
|---|---|---|---|---|---|
| D1 | Hệ thống thiết kế (màu, chữ, khoảng cách, bo góc, nút, trạng thái) + làm lại trang chủ, thẻ, trang chi tiết, giỏ | Đẹp, chuyên nghiệp, dễ mua | L | Ảnh `screenshots/after/`, trang so sánh; Lighthouse mobile ≥ 90 cả 4 mục | ⬜ |
| E1 | Bảng size + link cạnh chỗ chọn size + gợi ý size theo chiều cao, cân nặng | Chọn đúng size | M | Kiểm thử mở đúng hãng, gợi ý đúng theo bảng | ⬜ |
| E2 | Lọc theo size còn hàng, khoảng giá, nhãn hiệu (nút "Lọc" trên điện thoại) | "Size 42 còn không" tự xem | M | Kiểm thử từng bộ lọc | ⬜ |
| E3 | Hỏi shop về SP: sao chép sẵn tên, mã, size | Khách không gõ lại | S | Kiểm thử clipboard | ⬜ |
| E4 | Khối "Ghé shop": bản đồ (tải khi kéo tới), chỉ đường, giờ mở cửa, nút gọi (ẩn tới khi có số, Q2) | Khách tìm tới shop | S | Kiểm thử | ⬜ |
| E5 | Đặt đồng phục đội: chọn mẫu, số lượng theo size, tên + số in áo, tin nhắn Zalo | Đơn lớn | M–L | Kiểm thử tạo tin nhắn đúng | ⬜ |
| E6 | Sản phẩm liên quan, đã xem gần đây | Xem thêm hàng | S | Kiểm thử | ⬜ |
| E7 | Yêu thích (lưu trên máy), chia sẻ SP | Quay lại mua | S | Kiểm thử | ⬜ |
| E8 | Mã QR từng SP (trong trang quản trị) và tấm QR in dán ở shop dẫn về web | Khách tại shop vào web | S | Tệp in được, quét ra đúng link | ⬜ |
| E9 | Cài web như ứng dụng (manifest, biểu tượng) | Khách quay lại dễ | S | Lighthouse nhận diện được | ⬜ |
| E10 | Trợ lý chọn đồ theo kịch bản (không AI) | Khách mới dễ chọn | M | Kiểm thử các nhánh | ⬜ |

## Lỗi còn lại (từ AUDIT)
| Mã | Lỗi | Độ khó | TT |
|---|---|---|---|
| L14 | Địa chỉ lỗi mã hóa làm máy chủ Node báo 500 | S | ⬜ |
| L17 | Admin bản Node nhận `.xlsx` nhưng báo lỗi chung chung | S | ⬜ |

Các mục đã xong trước đó: xem PROGRESS.md.

## Chủ shop đã duyệt (24/11/2026)
- Duyệt từ PROPOSALS.md: **A1–A7, B1–B6, C1, C3, D1–D7, E2** (hợp nhất về một giao diện Next.js xuất web tĩnh; bản HTML giữ làm dự phòng, chưa xóa). Đồng ý tải JDK + Maven bản di động, miễn phí, vào thư mục tạm để đối chiếu Python–Java (A2). Không đưa thẻ tích điểm lên web.
- Việc mới:
  | Mã | Việc | Lợi ích | Độ khó | Xong khi… | TT |
  |---|---|---|---|---|---|
  | N1 | Sao chép đơn và mở Zalo/Messenger **kèm hình sản phẩm**. Trên điện thoại dùng nút "Chia sẻ" của máy (gửi được cả ảnh lẫn chữ sang Zalo/Messenger); máy không hỗ trợ thì tin nhắn kèm link ảnh từng món. Cần có ảnh thật (A1) | Shop nhìn ảnh là biết đúng món | M | Kiểm thử trên điện thoại giả lập: chia sẻ có ảnh + chữ; dự phòng có link ảnh | ⬜ |
  | N2 | Làm lại giao diện trang quản trị cho dễ nhìn (theo hệ thống thiết kế D1, hai bản sao giống nhau) | Chủ shop thao tác nhanh, ít nhầm | M | Ảnh trước–sau; Playwright quản trị đạt ở máy tính, điện thoại, sáng, tối | ⬜ |

## Ghi chú vận hành
- Lần chạy đợt 1 bằng agent song song (24/11) **không ra kết quả**: tạo worktree bị lỗi đọc cấu hình git, rồi chạm giới hạn 5 giờ. Không có thay đổi nào trong mã. Lần sau chạy từng việc tuần tự, không dùng worktree.
