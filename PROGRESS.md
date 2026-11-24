# Tiến độ – SPORT 238

Cách làm tiếp: đọc tệp này → `CLAUDE.md` → `AUDIT.md` → `PROPOSALS.md`. Quy trình 7 giai đoạn do chủ shop đặt (khảo sát → đề xuất, **dừng chờ duyệt** → sửa lỗi → giao diện, **dừng chờ duyệt** → chức năng mới → nhập hàng Sapo → kiểm thử/CI → đưa lên mạng). Sau mỗi việc: kiểm thử, cập nhật tệp này, commit.

## Cách làm để tiết kiệm lượt dùng (chủ shop duyệt 24/11/2026)
- Làm tuần tự từng việc, không chạy hàng chục agent cùng lúc; không dùng git worktree (đang lỗi đọc cấu hình git trên máy này).
- Agent phụ mặc định chạy Sonnet (`CLAUDE_CODE_SUBAGENT_MODEL=sonnet` trong `~/.claude/settings.json`). Việc chỉ đọc, tìm kiếm, chép số liệu: dùng agent `doc-nhanh` (Haiku, `.claude/agents/doc-nhanh.md`). Opus chỉ cho việc lập trình khó.

## TIẾN ĐỘ HIỆN TẠI (cập nhật 24/11/2026 chiều) — đọc phần này trước
Chủ shop đã duyệt PROPOSALS: **A1–A7, B1–B6, C1, C3, D1–D7, E2**; việc mới **N1** (gửi đơn kèm hình SP), **N2** (giao diện trang quản trị dễ nhìn). Không đưa thẻ tích điểm lên web. Câu hỏi còn mở: `QUESTIONS.md`.
- ✅ **A1** nạp ảnh hàng loạt theo SKU (`sport-shop-app/tools/nap_anh.py`, `nap-anh.bat`; pytest `tests/py/test_nap_anh.py`).
- ✅ **A7** lỗi L14, L17 (pytest `tests/py/test_server.py`).
- ✅ **A2** danh mục "Giày thể thao" (Python 2 bản + Java; `ParityWithPythonTest` Python = Java trên file thật; dữ liệu mẫu cập nhật).
- ✅ **E2** Next.js xuất web tĩnh là bản chính (`tools/export_next.py`, `daily_update.xuat_web` tự dùng HTML khi lỗi; `tests/test_seo.py`). Nhãn `on-dinh-2026-11-24-e2-next-tinh`. **Từ nay chức năng và giao diện mới chỉ làm trên Next.js** (xem CLAUDE.md).
- ✅ **T (một phần)** `tests/test_a11y.py` (axe) + `tests/lighthouse.py`; cài: `cd tests && npm install`. ✅ **D5** axe 0 lỗi serious trên cả hai bản. Lighthouse: trang SP 98/100/100/100; trang chủ hiệu năng ~70 (xem phân tích trong BACKLOG: phần lớn do chi phí phông chữ của máy đo Windows).
- ✅ **D1–D4, D7 (24/11/2026 tối) – làm lại giao diện bản Next.js:** hệ thống thiết kế viết lại gọn ở đầu `app/globals.css` (biến màu theo logo + bản tối đủ tương phản, thang chữ, khoảng cách, bo góc, bóng, nút và trạng thái); biểu tượng SVG `components/Icons.tsx` (bỏ emoji trang trí, dải chữ chạy, biểu tượng bay, backdrop-filter); chưa có ảnh thật thì hiện **hình minh họa SVG theo danh mục, tô theo màu sản phẩm** (`components/ArtSprite.tsx`, vẽ một lần mỗi trang); đầu trang gọn có nút tìm nhanh; phần mở đầu thấp (điện thoại 370 px) với thông điệp "Chọn size, nhắn Zalo, ghé shop nhận hàng" + giờ mở cửa; dải lợi ích; danh mục SVG (điện thoại vuốt ngang); trang chi tiết có ảnh vuốt (scroll-snap), **thanh "Thêm vào giỏ" dính đáy màn hình trên điện thoại** (gộp nút Zalo và giỏ, thay thanh dưới), khối "Ghé shop nhận hàng" (địa chỉ, giờ, chỉ đường Google Maps); giỏ gọn (tạm tính + 2 nút gửi đơn cố định ở cuối). Tốc độ: trang chủ gửi danh sách SP dạng gọn (`pack/unpack` trong `lib/shop.ts`), giỏ trống không tải `products.json`, logo 96 px WebP 3 KB, phông 3 độ đậm: trang chủ 235 KB → 138 KB. **Lighthouse (điện thoại, máy này): trang chủ 99/100/100/100 (trước 66–76 hiệu năng), trang SP 95–100/100/100/100.** Kiểm thử mới `tests/test_giao_dien.py` (65 mục), chụp ảnh `tests/chup_anh.py`, so sánh `screenshots/so-sanh.html`.
- ✅ **Sửa sau rà soát giao diện (24/11 tối, 13 phát hiện, 0 nặng):** dòng hãng trên thẻ không bị cắt (điện thoại chỉ hiện hãng), bỏ khoảng trống dưới tên ngắn, bỏ nút Zalo lặp ở phần mở đầu trên điện thoại, dải lợi ích căn đều, size hết hàng viền nét đứt, nút bỏ từng món trong giỏ, hình minh họa không in số, bỏ dòng lặp ý ở thẻ Ghé shop, cuộn tôn trọng "giảm chuyển động" (`scrollMode()`), cờ tìm nhanh hết hạn sau 3 giây, `key` cho trang chi tiết, xóa mã thừa. Kiểm thử: test_giao_dien thêm mục 8 (10 kiểm tra) → 0 lỗi; 4 bài cơ bản, axe, SEO 0 lỗi; pytest 28 đạt; Lighthouse trang chủ 99/100/100/100, trang SP 100/100/100/100. Chưa sửa (ghi lại): tên SP dạng "AMAC- Blur" (chủ shop đặt "Tên hiển thị", Q11); ngưỡng "Sắp hết" (Q12).
- ✅ **A3 + B1 bảng size và gợi ý size (24/11 tối):** dữ liệu `sport-shop-next/frontend/data/bang-size.json` (15 bảng, 9 hãng, chép 2 lần độc lập khớp 430/431 ô, ô còn lại theo ảnh); thuật toán tra bảng `lib/sizes.ts` (không AI; chiều cao/cân nặng lệch size: theo lời khuyên của hãng nếu có, không thì nói rõ cả hai); trang `/bang-size/`; nút "Bảng size … và gợi ý size" cạnh chỗ chọn size ở trang SP, tự đúng hãng, có "Chọn size X"; giày ghi chưa có bảng size (Q3); hãng chưa có bảng ghi rõ; link ở menu, chân trang, sitemap. Kiểm thử `tests/test_bang_size.py` 0 lỗi; toàn bộ bài khác 0 lỗi; pytest 28 đạt.
- ⏭ **Tiếp theo theo thứ tự:** A4, A5, A6, B2–B5, C1, C3, N1 → B6 + N2 (trang quản trị) → G (nhập hàng an toàn, BACKLOG) → T (axe, Lighthouse, CI) → J (hướng dẫn đưa lên mạng).
- Kiểm thử sau D1–D4 (web tĩnh Next 3702): test_all, test_feat, test_cards, test_mobile, test_giao_dien, test_a11y, test_seo đều 0 lỗi; pytest 28 đạt. Trước đó: pytest 28 bài đạt; test_seo 0 lỗi; 4 bài Playwright 0 lỗi trên web tĩnh Next (export_next + http.server 3602); trước đó: pytest 25 bài đạt (`py -m pytest`); `mvn test` 5 bài đạt (JDK/Maven di động ở `scratchpad/java`, có thể bị xóa — tải lại theo tests/README.md); 4 bài Playwright 0 lỗi trên Node 3000 và Next.js 3100.

## CHẾ ĐỘ TỰ CHỦ (từ 24/11/2026)
Chủ shop đã chuyển sang chế độ tự chủ tối đa: không dừng chờ duyệt; việc cần chủ shop quyết định ghi vào `QUESTIONS.md` (tạm chọn phương án an toàn) rồi làm tiếp. Danh sách việc và tiêu chí "xong khi…": `BACKLOG.md`. Nhãn bản ổn định trước đợt này: `on-dinh-2026-11-24-sau-sua-loi-dt`.
- **Đợt 1 (chạy song song 24/11 bị lỗi worktree + giới hạn lượt dùng, không có kết quả; nay làm tuần tự):** mỗi việc một nhánh `wf/…` (P1 Giày thể thao + pytest + đối chiếu Java; F nạp ảnh + quản trị; G nhập hàng an toàn; H Next.js xuất tĩnh; T axe/Lighthouse/CI; J hướng dẫn đưa lên mạng) + khảo sát sâu K1, ý tưởng K2, chép bảng size S1. Sau khi xong: gộp từng nhánh vào `dev`, chạy toàn bộ kiểm thử, cập nhật AUDIT/BACKLOG.
- **Đợt 2 (tiếp theo):** làm lại giao diện (hệ thống thiết kế) + chức năng mới cho khách trên bản chính.

## Đang ở đâu (cập nhật 24/11/2026, trước chế độ tự chủ)
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
