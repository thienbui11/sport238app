# BACKLOG – SPORT 238

Xếp theo lợi ích ÷ công sức (cao trước). Độ khó: S < nửa ngày, M 1–2 ngày, L ≥ 3 ngày. Trạng thái: ⬜ chưa làm · 🔄 đang làm · ✅ xong.
"Xong khi…" luôn gồm tiêu chuẩn chung: kiểm thử Playwright đạt ở máy tính và điện thoại 390 px, sáng và tối; không lỗi console, không tràn ngang; axe 0 lỗi nghiêm trọng; không lộ giá nhập; chữ tiếng Việt đúng.

## Đợt 1 – nền tảng (chạy song song, mỗi việc một nhánh)
| Mã | Việc | Lợi ích | Độ khó | Xong khi… | TT |
|---|---|---|---|---|---|
| K1 | Khảo sát sâu: trang quản trị, cập nhật hằng ngày, xuất web tĩnh, bảo mật | Biết hết lỗi còn lại | M | AUDIT.md có mục quản trị, vận hành, bảo mật; ảnh trang quản trị trong `screenshots/before/` | ⬜ |
| K2 | Tìm ý tưởng từ các shop thể thao, trang bán hàng tốt | Chọn đúng việc đáng làm | S | Có danh sách ý tưởng kèm nguồn, đã đưa vào backlog | ⬜ |
| P1 | Danh mục "Giày thể thao" (Python + Java), pytest cho bộ đọc Excel, đối chiếu Python–Java trên file thật | Khách tìm giày đúng chỗ; nhập hàng an toàn | M | pytest đạt; Python = Java trên file 14/11 (175 SP, 953 phiên bản, 632 dòng, bỏ 68); 9 danh mục ở cả hai giao diện và trang quản trị | ✅ |
| F1 | Nạp ảnh hàng loạt theo mã SKU (thu nhỏ, WebP, theo màu, báo cáo HTML) | Có ảnh thật nhanh | M | Lệnh chạy với thư mục mẫu: ảnh đúng SP/màu, giữ ảnh cũ, báo tệp sai mã, báo SP thiếu ảnh; có kiểm thử | ✅ |
| F2 | Trang quản trị: lọc hết hàng / chưa mô tả / chưa ảnh, sửa hàng loạt (ẩn, nổi bật, danh mục), ảnh tải lên đổi WebP | Chủ shop đỡ tốn thời gian | M | Playwright cho từng thao tác; hai bản sao admin giống nhau | ✅ `tests/test_admin.py` |
| G1 | Nhập hàng mỗi ngày: nhận file mới trong Tải về (chép, không xóa), kiểm tra file (thiếu cột, số SP giảm bất thường → dừng), sao lưu trước khi nhập, quay lại bản trước, báo cáo thay đổi HTML, một nút làm hết, hướng dẫn Task Scheduler, tìm hiểu API Sapo | Cập nhật hằng ngày an toàn, ít thao tác | M–L | pytest cho kiểm tra file, báo cáo, sao lưu/khôi phục; chạy thật với file 14/11 trên dữ liệu thử | ✅ `tests/py/test_nhap_an_toan.py` |
| H1 | Next.js xuất web tĩnh: mỗi SP một trang (tiêu đề, mô tả, Open Graph, dữ liệu cấu trúc), sitemap, robots, tự chép ảnh, font chạy không cần mạng; không đưa trang quản trị ra ngoài | Một bản giao diện; Google và Zalo thấy từng SP | M–L | 4 bài kiểm thử cũ đạt trên thư mục xuất; có kiểm thử trang SP, meta, sitemap | ✅ |
| S1 | Chép bảng size từ ảnh chủ shop gửi (2 người chép độc lập, đối chiếu) | Dữ liệu cho bảng size, gợi ý size | S | Tệp dữ liệu bảng size khớp ảnh 100%; hãng thiếu ghi rõ | ⬜ |
| T1 | Kiểm thử axe + Lighthouse tự động, GitHub Actions (chưa push) | Giữ chất lượng lâu dài | M | Lệnh chạy được trên máy; có số liệu nền; tệp CI sẵn sàng | ✅ `tests/chay_tat_ca.py`, `.github/workflows/kiem-thu.yml` (chưa đẩy) |
| J1 | Hướng dẫn đưa lên mạng miễn phí (điều khoản hiện hành, Cloudflare Pages, tên miền, HTTPS, thống kê) | Chủ shop tự đưa lên được | S–M | HUONG-DAN-DUA-LEN-MANG.md viết lại, có nguồn, lệnh đưa lên tự động | ✅ (chưa đưa lên mạng) |

## Đợt 2 – giao diện và chức năng cho khách (trên bản chính sau khi hợp nhất)
| Mã | Việc | Lợi ích | Độ khó | Xong khi… | TT |
|---|---|---|---|---|---|
| D1 | Hệ thống thiết kế (màu, chữ, khoảng cách, bo góc, nút, trạng thái) + làm lại trang chủ, thẻ, trang chi tiết, giỏ | Đẹp, chuyên nghiệp, dễ mua | L | Ảnh `screenshots/after/`, trang so sánh; Lighthouse mobile ≥ 90 cả 4 mục | ✅ 24/11: trang chủ 99/100/100/100, trang SP 95–100/100/100/100 |
| E1 | Bảng size + link cạnh chỗ chọn size + gợi ý size theo chiều cao, cân nặng | Chọn đúng size | M | Kiểm thử mở đúng hãng, gợi ý đúng theo bảng | ✅ 24/11 |
| E2 | Lọc theo size còn hàng, khoảng giá, nhãn hiệu (nút "Lọc" trên điện thoại) | "Size 42 còn không" tự xem | M | Kiểm thử từng bộ lọc | ⬜ |
| E3 | Hỏi shop về SP: sao chép sẵn tên, mã, size | Khách không gõ lại | S | Kiểm thử clipboard | ⬜ |
| E4 | Khối "Ghé shop": bản đồ (tải khi kéo tới), chỉ đường, giờ mở cửa ~~nút gọi~~ (Q2: không làm) | Khách tìm tới shop | S | Kiểm thử | 🔄 trang SP đã có địa chỉ, giờ, chỉ đường Google Maps; còn bản đồ nhúng |
| E5 | Đặt đồng phục đội: chọn mẫu, số lượng theo size, tên + số in áo, tin nhắn Zalo | Đơn lớn | M–L | Kiểm thử tạo tin nhắn đúng | ⬜ |
| E6 | Sản phẩm liên quan, đã xem gần đây | Xem thêm hàng | S | Kiểm thử | ⬜ |
| E7 | Yêu thích (lưu trên máy), chia sẻ SP | Quay lại mua | S | Kiểm thử | ⬜ |
| E8 | Mã QR từng SP (trong trang quản trị) và tấm QR in dán ở shop dẫn về web | Khách tại shop vào web | S | Tệp in được, quét ra đúng link | ⬜ |
| E9 | Cài web như ứng dụng (manifest, biểu tượng) | Khách quay lại dễ | S | Lighthouse nhận diện được | ⬜ |
| E10 | Trợ lý chọn đồ theo kịch bản (không AI) | Khách mới dễ chọn | M | Kiểm thử các nhánh | ⬜ |

## Lỗi còn lại (từ AUDIT)
| Mã | Lỗi | Độ khó | TT |
|---|---|---|---|
| L14 | Địa chỉ lỗi mã hóa làm máy chủ Node báo 500 | S | ✅ |
| L17 | Admin bản Node nhận `.xlsx` nhưng báo lỗi chung chung | S | ✅ |

Các mục đã xong trước đó: xem PROGRESS.md.

## Chủ shop đã duyệt (24/11/2026)
- Duyệt từ PROPOSALS.md: **A1–A7, B1–B6, C1, C3, D1–D7, E2** (hợp nhất về một giao diện Next.js xuất web tĩnh; bản HTML giữ làm dự phòng, chưa xóa). Đồng ý tải JDK + Maven bản di động, miễn phí, vào thư mục tạm để đối chiếu Python–Java (A2). Không đưa thẻ tích điểm lên web.
- Việc mới:
  | Mã | Việc | Lợi ích | Độ khó | Xong khi… | TT |
  |---|---|---|---|---|---|
  | N1 | Sao chép đơn và mở Zalo/Messenger **kèm hình sản phẩm**. Trên điện thoại dùng nút "Chia sẻ" của máy (gửi được cả ảnh lẫn chữ sang Zalo/Messenger); máy không hỗ trợ thì tin nhắn kèm link ảnh từng món. Cần có ảnh thật (A1) | Shop nhìn ảnh là biết đúng món | M | Kiểm thử trên điện thoại giả lập: chia sẻ có ảnh + chữ; dự phòng có link ảnh | ✅ `tests/test_pwa_anh.py` |
  | N2 | Làm lại giao diện trang quản trị cho dễ nhìn (theo hệ thống thiết kế D1, hai bản sao giống nhau) | Chủ shop thao tác nhanh, ít nhầm | M | Ảnh trước–sau; Playwright quản trị đạt ở máy tính, điện thoại, sáng, tối | ✅ |

## Ghi chú vận hành
- Lần chạy đợt 1 bằng agent song song (24/11) **không ra kết quả**: tạo worktree bị lỗi đọc cấu hình git, rồi chạm giới hạn 5 giờ. Không có thay đổi nào trong mã. Lần sau chạy từng việc tuần tự, không dùng worktree.

## Số liệu nền (24/11/2026, bản Next.js xuất tĩnh, trước khi làm lại giao diện)
- Lighthouse điện thoại – trang chủ: hiệu năng **66** (tổng thời gian chặn 4,2 s: chuyển động chạy liên tục, tính kiểu/bố cục nặng, dữ liệu 175 SP nhúng vào trang), truy cập 100, thực hành tốt 100, SEO 100. Trang SP: 98 / 95 / 100 / 100.
- axe: 17 lỗi serious (3 loại) → **đã sửa, 0 lỗi** trên cả hai bản: nhãn link ảnh SP và nút size không khớp chữ hiển thị; tương phản chữ đỏ nhỏ trên nền tối (.eyebrow, giá), chữ "hết" của size hết hàng bị mờ.
- **Phân tích hiệu năng trang chủ (24/11/2026):** điểm 66–72 trên máy này. Bản ghi hiệu năng (CPU chậm 4 lần) cho thấy một lần tính bố cục 0,9–1,1 s; **trang 404 trống cũng tốn ~0,5 s** → phần lớn là chi phí cố định của Chrome khởi tạo phông chữ Windows lúc đo, không phải do trang. Đã thử và loại trừ: tắt chuyển động, bỏ làm mờ nền, ẩn emoji, phông hệ thống, chỉ gửi 20 SP (75 điểm). Bỏ hẳn emoji giảm ~120 ms; `content-visibility` giảm ~170 ms (trong sai số đo). Việc nên làm trong D1: thay emoji bằng biểu tượng SVG, ảnh WebP tải lười; **đo lại bằng PageSpeed Insights sau khi đưa lên mạng** hoặc Lighthouse trong CI Linux (số liệu thật hơn máy Windows này). Trang sản phẩm: 98 điểm.

## Số liệu sau khi làm lại giao diện (D1–D4, 24/11/2026 tối, web tĩnh Next + python http.server, không nén)
- Lighthouse điện thoại – trang chủ: **99 / 100 / 100 / 100** (FCP 1,7 s, LCP 1,7 s, TBT 60 ms, CLS 0); trang SP: **95–100 / 100 / 100 / 100**. Ba lần đo trang chủ đều 99.
- Nguyên nhân chính trước đây không phải chỉ do phông chữ: trang chủ nhúng toàn bộ 175 SP dạng đầy đủ (235 KB HTML) + emoji + chuyển động liên tục. Nay: danh sách SP gửi dạng gọn (138 KB HTML), SVG thay emoji, không chuyển động lặp, giỏ trống không tải `products.json`.
- axe: 0 lỗi (kể cả mức nhẹ). CLS = 0. Không tràn ngang ở 320/390/768/1366 px.
