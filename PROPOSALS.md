# PROPOSALS – Đề xuất cải tiến web SPORT 238 (Giai đoạn 1, 24/11/2026)

**Cách duyệt:** trả lời bằng mã mục (ví dụ "Duyệt A1–A6, B2, B3, E2; bỏ B5"). Sau đó tôi lập `PLAN.md` đúng các mục được chọn, mỗi việc có tiêu chí "xong khi…".

Mỗi mục ghi: **lợi ích** (cho khách hay chủ shop), **độ khó** (S: dưới nửa ngày · M: 1–2 ngày · L: 3 ngày trở lên), **rủi ro**, **cần anh/chị cung cấp gì**. Các mục được xếp theo "lợi ích ÷ công sức".
Đã xong ở đợt sửa lỗi 24/11 (không cần duyệt lại): điện thoại 2 cột, menu, tìm không dấu, quay lại đúng chỗ, nút ≥ 44 px, giữ màu/size, hỏi lại khi xóa giỏ, cảnh báo vượt tồn, giờ mở cửa, đăng xuất quản trị. Xem `screenshots/so-sanh.html`.

---
## TÌNH TRẠNG (cập nhật 24/11/2026 tối)

> **Các chức năng mới nằm ở bản chính (Next.js).** Trang `http://localhost:3000` (mở cùng trang quản trị) là **bản HTML dự phòng cũ**, không có các chức năng này.
> Muốn xem đúng bản khách sẽ thấy: bấm `cap-nhat-web.bat` rồi `xem-web.bat` (mở `http://localhost:8080`).

| Mã | Tình trạng | Xem ở đâu |
|---|---|---|
| A1 | ✅ Xong | `nap-anh.bat` (kéo thả thư mục ảnh đặt tên theo mã SKU) |
| A2 | ✅ Xong | Danh mục "Giày thể thao" |
| **A3** | ✅ Xong | Trang **Bảng size** (`/bang-size/`, có ở menu và chân trang); ở trang sản phẩm có nút "Bảng size … và gợi ý size" ngay cạnh chỗ chọn size |
| **A4** | ✅ Xong | Trang sản phẩm: "Hỏi qua Zalo" (sao chép sẵn câu hỏi), "Hỏi qua Messenger" (**điền sẵn** câu hỏi) |
| A5 | ✅ Xong (không có nút gọi – Q2) | Khối "Ghé shop nhận hàng": bản đồ, chỉ đường, giờ mở cửa |
| A6 | ✅ Xong; **lọc giá nay luôn hiện** cả trên điện thoại | Ô "Mọi mức giá" cạnh ô tìm kiếm |
| A7 | ✅ Xong | – |
| **B1** | ✅ Xong | Nhập chiều cao, cân nặng ở trang sản phẩm hoặc trang Bảng size → gợi ý size theo bảng của hãng |
| B2 | ✅ Xong | Trang **Đặt đồng phục đội** (`/dat-doi/`) |
| **B3** | ✅ Xong | Mỗi sản phẩm một trang riêng `/san-pham/<MÃ>/` (dán link vào Zalo/Facebook hiện tên, giá) |
| **B4** | ✅ Xong | Trang sản phẩm: "Sản phẩm cùng loại", "Bạn đã xem gần đây" (cả ở trang chủ) |
| **B5** | ✅ Xong | Nút chia sẻ ở trang sản phẩm |
| **B6** | ✅ Xong | Trang quản trị mới: lọc Hết hàng / Chưa có ảnh / Chưa có mô tả, xếp theo tồn, sửa hàng loạt |
| **B7** | ✅ Xong | Mỗi lần bấm `cap-nhat-web.bat`: báo cáo thay đổi tự mở (thư mục `bao-cao`) |
| B8 | ⬜ Chưa duyệt | – |
| B9 | ✖ Không đưa lên web (anh/chị quyết định) | – |
| C1 | ✅ Xong | Trái tim "Yêu thích" trên sản phẩm, lọc "Yêu thích" |
| **C3** | ⬜ **Chưa làm** – tôi đã nhầm làm C4 thay cho C3. Sẽ làm tiếp (bản đơn giản: hỏi cần gì → cho ai → size/chiều cao → tầm giá → ra danh sách còn hàng). Không hỏi "đá sân gì" được vì tên giày trong Sapo không ghi loại sân (chỉ 1/33 đôi có "TF") | – |
| C4 | ✅ Đã làm (ngoài danh sách duyệt) | Cài web lên màn hình điện thoại |
| D1–D7, E2 | ✅ Xong | Ảnh trước–sau: `screenshots/so-sanh.html` |

**Tự dán đơn và ảnh vào khung chat (yêu cầu 24/11):** trình duyệt **không cho** trang web tự dán vào ứng dụng khác, và Zalo **không có** link điền sẵn tin nhắn. Đã làm cách gần nhất:
- **Messenger:** nút "Mở Messenger (đơn điền sẵn)" mở khung chat có sẵn đơn (link `m.me/Sport238?text=…`, theo tài liệu của Meta), khách chỉ bấm Gửi. Messenger không nhận ảnh qua link. Nguồn: [Meta – m.me Links](https://developers.facebook.com/docs/messenger-platform/discovery/m-me-links).
- **Điện thoại (Zalo, Messenger…):** nút "Gửi đơn qua Zalo, Messenger… (điền sẵn)" mở bảng Chia sẻ của máy; chọn Zalo → chọn Sport 238 → Gửi. Chữ đơn **và ảnh từng món** (khi đã nạp ảnh) được đưa vào sẵn, không cần dán.
- **Zalo trên máy tính:** vẫn phải dán (Ctrl+V); đơn được sao chép sẵn khi bấm nút.

---
## ĐỀ XUẤT MỚI (đợt 2, 24/11/2026 tối) – chờ anh/chị duyệt

| Mã | Việc | Lợi ích | Độ khó | Cần anh/chị |
|---|---|---|---|---|
| **M1** | **Hẹn giờ ghé lấy hàng** trong giỏ: chọn ngày và giờ (trong 8:00–21:00) → tin nhắn ghi "Mình ghé lấy lúc 17:30, thứ Bảy 29/11" | Shop chuẩn bị sẵn hàng, khách đến không phải chờ | S | – |
| **M2** | **"Đang mở cửa · đóng lúc 21:00" / "Đã đóng cửa · mở lại 8:00"** theo giờ thật, ở đầu trang và khối Ghé shop | Khách biết lúc nào ghé được | S | – |
| **M3** | **Hàng mới về**: sản phẩm mới xuất hiện trong file Sapo có nhãn "Mới" 14 ngày và một mục "Hàng mới về" ở trang chủ (tự động từ báo cáo nhập) | Khách quen có lý do quay lại web | S–M | – |
| **M4** | **"Báo mình khi có hàng"** ở size/sản phẩm hết hàng: Messenger điền sẵn "Shop báo mình khi … size 42 về nhé" | Không mất khách khi hết size | S | – |
| **M5** | **Mã QR dán tại shop** (BACKLOG E8): tấm A5 có QR về web + tem QR từng sản phẩm dán lên kệ/móc áo → khách quét xem size còn, đặt giữ | Khách tại shop vào web, đặt lần sau | S–M | In và dán |
| **M6** | **Gợi ý mua kèm** trong giỏ và trang SP: áo → vớ/tất; giày → vớ, bó gối, túi rút (chỉ hàng còn trong shop) | Giỏ hàng lớn hơn | S | – |
| **M7** | **Tìm theo tên CLB, tên gọi quen**: gõ "mu", "man u", "real", "barca", "đội tuyển"… ra đúng áo; gợi ý ngay khi gõ | Khách tìm áo CLB nhanh | S–M | – |
| **M8** | **Gửi link giỏ hàng/đơn đội**: đội trưởng gom size cả đội, gửi một link cho đồng đội kiểm tra hoặc gửi shop (mở link là thấy đúng giỏ) | Đặt đội dễ hơn | S–M | – |
| **M9** | **Khối khuyến mãi bật/tắt trong trang quản trị**: chỉ hiện đúng chữ anh/chị nhập (không tự bịa), có ngày hết hạn tự ẩn | Chạy khuyến mãi mùa giải không cần sửa mã | M | Nội dung khuyến mãi khi có |
| **M10** | **"Bán nhiều tuần này"** ước tính từ tồn kho giảm giữa các lần nhập Excel (ghi rõ "theo tồn kho") | Khách thấy món được ưa chuộng | M | Đồng ý cách tính |
| **M11** | **In bảng giá / tem giá** theo danh mục từ trang quản trị (A4, có QR) | Treo tại shop, đồng bộ giá với web | S | – |
| **M12** | **Hồ sơ Google Maps (Google Business Profile)**: hướng dẫn hoàn thiện, link "Đánh giá trên Google" thật | Khách quanh KCN tìm thấy shop trên Maps | S (anh/chị tự làm theo hướng dẫn) | Tài khoản Google |

Ý tưởng **không nên làm**: thanh toán online (trái quy tắc shop), "có X người đang xem"/đánh giá tự tạo (thông tin không thật), tự đăng bài Facebook/Zalo (cần API, dễ bị khóa trang).

---
## LÀM NGAY

| Mã | Việc | Lợi ích | Độ khó | Rủi ro | Cần anh/chị |
|---|---|---|---|---|---|
| **A1** | **Nạp ảnh hàng loạt theo mã SKU** *(anh/chị đã yêu cầu)*. Lệnh `nap-anh` đọc một thư mục: `PVN3939.jpg` là ảnh chính, `PVN3939-1.jpg`, `-2`… là ảnh phụ. Mã là của phiên bản nên tự biết ảnh thuộc **màu nào**. Tự thu nhỏ (≤ 1400 px), đổi WebP, nạp vào trang quản trị, giữ ảnh cũ. Kèm báo cáo HTML: đã nạp bao nhiêu, tên tệp không khớp mã nào, sản phẩm còn thiếu ảnh (xếp theo tồn kho) | Khách: thấy hàng thật, tin tưởng hơn rất nhiều (hiện 0/175 SP có ảnh). Chủ shop: không phải bấm từng sản phẩm | M | Ảnh chụp điện thoại rất nặng: công cụ tự nén. Tên tệp sai mã thì báo, không nạp nhầm | Đường dẫn thư mục ảnh; 20–30 SP bán chạy đầu tiên |
| **A2** | **Danh mục mới "Giày thể thao"** *(anh/chị đã duyệt)*, tách giày vải, giày thể dục khỏi "Giày bóng đá". Sửa quy tắc ở cả Python lẫn Java, đối chiếu trên file Sapo thật, cập nhật CLAUDE.md (8 → 9 danh mục). Danh mục chỉnh tay trong trang quản trị vẫn được giữ | Khách tìm giày thường thấy ngay | S–M | Bản Java chưa chạy được trên máy (chưa có Java). Muốn đối chiếu Python–Java phải tải JDK + Maven **bản di động, miễn phí** vào thư mục tạm (lần trước đã làm như vậy) | Đồng ý cho tải JDK/Maven di động; xác nhận tên danh mục "Giày thể thao" |
| **A3** | **Bảng size** *(anh/chị đã yêu cầu)*. Trang "Bảng size" chia theo hãng: RIKI, Win, Strivend, Bulbal, AMAC (người lớn, trẻ em), Just Play (người lớn, trẻ em), Kaiwin, Sao Việt, Egan. Số liệu chép đúng từ ảnh anh/chị gửi, **không tự bịa**. Hãng chưa có bảng thì ghi rõ "Chưa có bảng size, nhắn shop để được tư vấn". Ở trang sản phẩm có link "📏 Bảng size" **ngay cạnh chỗ chọn size**, tự mở đúng hãng của sản phẩm | Khách tự chọn đúng size, bớt hỏi đi hỏi lại, bớt đổi hàng | M | Nhiều bảng của cùng một hãng khác nhau (RIKI có 2 bảng, Bulbal có 2 mẫu): ghi theo mẫu áo | Bảng size **giày**; bảng của CV, HD Sport, Wika, Mira, Peace Max (nếu có); 2 bảng không ghi tên hãng (nền vàng "S < 165 cm" và nền trắng "1m50–1m55") là của hãng nào |
| **A4** | **"Hỏi shop về sản phẩm này" sao chép sẵn** câu hỏi: "Shop ơi, mình hỏi về [tên] – mã [PVN…], size [..]" rồi mở Zalo/Messenger (giống giỏ hàng) | Khách không phải gõ lại; shop biết ngay khách hỏi món nào | S | Không | – |
| **A5** | **Khối "Ghé shop"** ở trang chủ và trang chi tiết: bản đồ Google (nhúng miễn phí, không cần khóa API), nút "Chỉ đường", giờ mở cửa, nút **Gọi điện** | Khách ở gần KCN tìm đường, gọi hỏi nhanh | S | Bản đồ nhúng làm trang nặng hơn: chỉ tải khi kéo tới | Số 0962 374 770 có nhận **cuộc gọi thường** không, hay chỉ Zalo? |
| **A6** | **Lọc theo size còn hàng** (ví dụ "Size 42" chỉ hiện giày còn size 42), **khoảng giá**, **nhãn hiệu**. Trên điện thoại gom vào một nút "Lọc" | Khách hỏi nhiều nhất là "size này còn không": tự xem được | M | Không | – |
| **A7** | Sửa lỗi nhỏ còn lại trong AUDIT: L14 (địa chỉ lỗi làm máy chủ báo 500), L17 (trang quản trị bản Node nhận nhầm `.xlsx`: báo rõ "chạy nút cập nhật" thay vì lỗi chung chung) | Ổn định | S | Không | – |

## NÊN LÀM

| Mã | Việc | Lợi ích | Độ khó | Rủi ro | Cần anh/chị |
|---|---|---|---|---|---|
| **B1** | **Gợi ý size theo chiều cao, cân nặng** (không dùng AI, tra bảng size của A3): khách nhập "1m70, 65 kg" → "RIKI: size L; AMAC: size L". Có ở trang sản phẩm và trang bảng size | Khách chọn size tự tin; lợi thế so với shop chỉ đăng ảnh bảng size | M | Bảng các hãng chồng lấn: hiện "giữa M và L, nên chọn L" theo lời khuyên in trên bảng (AMAC, Just Play) | Làm sau A3 |
| **B2** | **Đặt đồng phục đội**: chọn mẫu áo (danh mục "Quần áo không logo"), nhập số lượng theo từng size, bảng tên + số in áo từng cầu thủ, ghi chú logo đội, rồi tạo tin nhắn Zalo đầy đủ. Tạm tính chỉ theo giá lẻ đang bán; giá in và chiết khấu đội ghi "shop báo giá" | Đơn đội nhóm là đơn lớn; hiện chỉ có nút "Nhắn Zalo tư vấn" | M–L | Tin nhắn dài: chia gọn, kèm bảng | Giá in tên số (hay để "shop báo giá"), số lượng tối thiểu, thời gian làm, có in logo không |
| **B3** | **Trang riêng cho từng sản phẩm** khi xuất web tĩnh: link `…/san-pham/PVN3939/` có tên, giá, ảnh khi dán vào Zalo/Facebook; Google đọc được từng sản phẩm; có `sitemap.xml` (sửa L16) | Chia sẻ sản phẩm cho khách qua Zalo đẹp và đúng món; khách tìm trên Google thấy shop | M | Phụ thuộc E1/E2 (cách làm khác nhau tùy kiến trúc) | Tên miền (khi đưa lên mạng) |
| **B4** | **Sản phẩm liên quan** (cùng danh mục, cùng hãng, còn hàng) và **đã xem gần đây** (lưu trên máy khách) ở trang chi tiết | Khách xem thêm hàng, giỏ to hơn | S | Không | – |
| **B5** | **Nút chia sẻ** sản phẩm (chia sẻ của điện thoại, hoặc sao chép link) | Khách gửi cho bạn bè, đội bóng | S | Đẹp nhất khi có B3 | – |
| **B6** | **Trang quản trị nhanh hơn**: lọc "đang hết hàng", "chưa có ảnh" xếp theo tồn kho; sửa hàng loạt (ẩn, danh mục, nổi bật cho nhiều SP một lúc); xem trước ảnh to | Chủ shop đỡ mất thời gian | M | Không | – |
| **B7** | **Báo cáo thay đổi sau mỗi lần nhập Excel** (HTML): SP mới, vừa hết hàng, đổi giá, chưa có ảnh, bị loại khỏi web. *(Thuộc Giai đoạn 5, nêu trước để anh/chị biết)* | Chủ shop nắm được web thay đổi gì mỗi ngày, phát hiện file lỗi | M | Không | – |
| **B8** | **Hàng hết lâu ngày**: tùy chọn ẩn SP hết hàng khỏi danh sách mặc định (vẫn tìm được, vẫn có lọc "Hết hàng") | Danh sách gọn (44/175 SP đang hết) | S | Khách không thấy hàng sắp về | Có muốn ẩn không? |
| **B9** | **Thẻ tích điểm** (mỗi 100k một ô; 5 ô: túi rút hoặc 2 cuộn keo nhỏ; 10 ô: bó gối/gót; 15 ô: túi 2 ngăn; 20 ô: bộ áo CLB/đội tuyển; không áp dụng hóa đơn đặt đội) ghi lên web | Khách có thêm lý do quay lại shop | S | Phải ghi đúng điều kiện | Xác nhận còn áp dụng và có muốn đưa lên web không |

## ĐỂ SAU

| Mã | Việc | Vì sao để sau |
|---|---|---|
| C1 | Danh sách yêu thích | Shop nhỏ, khách mua nhanh; "đã xem gần đây" (B4) đủ dùng |
| C2 | So sánh sản phẩm | Ít giá trị với đồ bóng đá giá phổ thông |
| C3 | Trợ lý chọn đồ theo kịch bản (hỏi đá sân gì, tầm giá…) | Làm sau khi có ảnh thật và bảng size; B1 giải quyết phần quan trọng nhất |
| C4 | Cài web lên màn hình điện thoại (PWA) | Lợi ích nhỏ với khách mua thưa |
| C5 | Lưu đơn đặt từ web vào trang quản trị | Web tĩnh không lưu được dữ liệu; cần máy chủ chạy suốt trên mạng, trái giới hạn "không tốn phí" |

---
## D. Cải tiến giao diện tổng thể (Giai đoạn 3, sẽ dừng chờ duyệt giao diện)
| Mã | Việc | Độ khó |
|---|---|---|
| D1 | Hệ thống thiết kế nhỏ: một bộ màu (đỏ đô, xám đen), cỡ chữ, khoảng cách, bo góc, bóng, trạng thái nút; viết lại `globals.css` gọn (bỏ CSS vá chồng, CSS thừa) | M |
| D2 | Thẻ sản phẩm gọn hơn khi có ảnh thật; trên điện thoại nút size thu gọn thành "Chọn size ▾" mở bảng chọn to (đỡ dài thẻ) | M |
| D3 | Trang chi tiết: ảnh lớn vuốt được, thanh "Thêm vào giỏ" dính đáy màn hình điện thoại, bảng size và "Ghé shop" ngay dưới | M |
| D4 | Tốc độ: logo nhúng 1 lần (bớt khoảng 70 KB), ảnh WebP tải lười, tải dữ liệu song song; mục tiêu Lighthouse mobile ≥ 90 (hiệu năng, truy cập, SEO) | S–M |
| D5 | Truy cập: kiểm bằng axe trong bài kiểm thử; tương phản mọi chữ (hiện chữ đỏ nhỏ trên nền tối chưa đạt) | S |
| D6 | SEO và chia sẻ: tiêu đề, mô tả từng trang, ảnh Open Graph, dữ liệu cấu trúc "cửa hàng địa phương" (địa chỉ, giờ mở cửa) cho Google Maps/Search | S (sau B3) |
| D7 | Ảnh trước–sau mọi trang, trang so sánh HTML | S |

## E. Đề xuất kiến trúc

**Hiện trạng:** hai bản giao diện (HTML thuần, React), hai bộ đọc Excel (Python, Java), và một backend Spring Boot chưa từng chạy thật. Đợt sửa lỗi vừa rồi tốn gần gấp đôi công vì phải làm hai lần, và vẫn có lúc hai bản lệch nhau.

| Phương án | Nội dung | Ưu | Nhược |
|---|---|---|---|
| **E1. Giữ nguyên** | Hai bản giao diện, hai bộ đọc Excel | Không phải chuyển đổi | Mọi việc làm 2 lần; dễ lệch; Java không chạy được trên máy shop |
| **E2. Một giao diện Next.js xuất web tĩnh** *(khuyên dùng)* | Dùng Next.js chế độ xuất tĩnh (`output: "export"`): mỗi sản phẩm có trang riêng (B3, D6), vẫn là tệp tĩnh đưa lên Cloudflare Pages miễn phí. Giữ trang quản trị + API Node (`sport-shop-app`) chạy trên máy shop làm nguồn dữ liệu. **Một bộ đọc Excel Python**; backend Spring Boot và `SapoParser.java` **để dành** (không xóa, không bắt buộc đồng bộ nữa) | Sửa 1 lần; mã có cấu trúc, TypeScript bắt lỗi; trang riêng từng SP cho Google và Zalo; bỏ được yêu cầu đối chiếu Java | Nút cập nhật phải chạy `npm run build` (khoảng 1 phút, máy đã có Node); phụ thuộc thư viện npm (cần cập nhật bảo mật định kỳ); chuyển đổi khoảng M (bản React đã giống bản HTML, đạt cả 4 bài kiểm thử) |
| **E3. Một giao diện HTML thuần** | Bỏ bản React; Python sinh thêm trang tĩnh cho từng sản phẩm | Không phụ thuộc thư viện nào; build tức thì | Mã giao diện dạng chuỗi trong một tệp, khó mở rộng khi thêm A6, B1, B2, D2; dễ lỗi hơn |

**Khuyên:** E2. Đây là việc "bỏ một bản giao diện" nên **cần anh/chị đồng ý**. Nếu duyệt E2, làm ở đầu Giai đoạn 2, **trước** A3–A6, để các chức năng mới chỉ phải làm một lần. Bản HTML hiện tại vẫn bán bình thường cho tới khi bản mới đạt đủ kiểm thử.

---
## Tham khảo (chỉ học ý tưởng)
- Baymard Institute, nghiên cứu trang bán quần áo. Điểm chính: nút size phải hiện sẵn (không giấu trong danh sách thả), đủ to trên điện thoại; link bảng size đặt ngay cạnh chỗ chọn size; bảng size đổi ra cỡ quen thuộc; nút Back phải về đúng trang trước.
  [apparel-5-best-practices](https://baymard.com/blog/apparel-5-best-practices) · [apparel-size-information](https://baymard.com/blog/apparel-size-information) · [use-buttons-for-size-selection](https://baymard.com/blog/use-buttons-for-size-selection) · [locating-the-size-guide](https://baymard.com/guidelines/2597-locating-the-size-guide)
- Mẫu đơn đặt đồ đội: cột tên, số áo, size, số lượng; giới hạn ký tự tên in (ví dụ tối đa 15 chữ).
  [Kitlocker team order form](https://www.kitlocker.com/clubhub/?p=2237) · [Tally soccer team form](https://tally.so/templates/soccer-team-t-shirt-order-form/nrYjNw) · [Team Spirit Sports – club kit order process](https://www.teamspiritsports.com.au/blog/club-kit-order-process) · [FORZA custom kits](https://www.forza.com/ie/custom-geo-mens-football-kits)
- Sapo: có tài liệu API cho sản phẩm, phiên bản ([support.sapo.vn/product-variant](https://support.sapo.vn/product-variant)) và API kho cho gói doanh nghiệp ([sapo.vn/blog/sapo-enterprise-api-tich-hop-du-lieu](https://sapo.vn/blog/sapo-enterprise-api-tich-hop-du-lieu)). **Chưa rõ** gói Sapo POS của shop có được dùng API không: sẽ kiểm tra kỹ ở Giai đoạn 5 (hỏi tổng đài Sapo), không đăng nhập tài khoản của anh/chị khi chưa hỏi.
