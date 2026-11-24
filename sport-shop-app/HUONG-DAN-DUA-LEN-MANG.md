# Đưa web SPORT 238 lên mạng và cập nhật hằng ngày

## 1. Cách hoạt động

- **Web công khai (khách xem)** là một thư mục tĩnh `dist/` (chỉ có chữ, ảnh, `products.json`). Không có máy chủ, không có cơ sở dữ liệu, nên rẻ, nhanh và rất ít chuyện hỏng. Khách chọn size, thêm giỏ, rồi bấm sao chép đơn và mở Zalo hoặc Messenger để nhắn shop.
- **Trang quản trị (chỉ bạn dùng)** chạy ngay trên máy tính ở shop (`chay-quan-tri.bat`). Ở đây bạn nhập hàng từ Sapo, thêm ảnh, sửa tên, mô tả, danh mục, ẩn hoặc đánh dấu nổi bật. Quản trị **không đưa lên mạng**, nên không ai tấn công được.
- Mỗi khi cần, bạn bấm **xuất web**: chương trình tạo ra `dist/` mới rồi đưa lên hosting.

Bản bán ngay hôm nay: giải nén `sport238-website.zip` (đã có 175 sản phẩm theo file Excel ngày 14/11/2026) và tải lên hosting theo mục 3. Chưa có ảnh sản phẩm, web sẽ hiện biểu tượng thay thế cho đến khi bạn thêm ảnh.

## 2. Cài trang quản trị trên máy shop (làm một lần)

1. Cài **Node.js 22.9 trở lên** (nodejs.org) và **Python 3.10 trở lên** (python.org, nhớ tích "Add to PATH").
2. Mở dòng lệnh, chạy: `pip install pandas openpyxl`
3. Giải nén `sport-shop-app.zip` vào một thư mục cố định, ví dụ `D:\sport238`.
4. Chép `.env.example` thành `.env` rồi sửa:
   - `ADMIN_PASSWORD` mật khẩu mạnh của bạn
   - `ZALO_PHONE=0962374770`, `MESSENGER_USER=Sport238`, `SHOP_NAME=SPORT 238`
   - `SITE_URL` địa chỉ web thật (điền sau khi có tên miền)
   - `DEPLOY_CMD` lệnh tự đưa lên hosting (xem mục 4, có thể để trống lúc đầu)
5. Bấm đúp `chay-quan-tri.bat`, giữ cửa sổ đó mở. Mở trình duyệt vào http://localhost:3000/admin.

## 3. Đưa web lên hosting (tên miền và HTTPS)

**Chọn nơi đặt web.** Web tĩnh đặt được hầu như ở đâu. Điều cần cẩn thận là điều khoản dùng cho mục đích bán hàng:
- **Vercel gói miễn phí (Hobby)**: điều khoản (cập nhật 1/6/2026) chỉ cho dùng cá nhân hoặc phi thương mại, và Vercel định nghĩa "thương mại" là bất kỳ bản triển khai nào phục vụ lợi ích tài chính của bất kỳ ai liên quan. Web giới thiệu hàng để khách mua hàng của shop thuộc trường hợp này, kể cả khi thanh toán không diễn ra trên web. Muốn dùng Vercel thì phải dùng gói Pro (trên trang Hobby của Vercel ghi mỗi người dùng 20 USD/tháng). Muốn chắc chắn hơn, hỏi thẳng bộ phận hỗ trợ của Vercel bằng văn bản.
- **GitHub Pages**: theo một bài so sánh hosting mình đọc, điều khoản không cho chạy web kinh doanh, bán hàng. Không nên dùng.
- **Cloudflare Pages (gói miễn phí)**: theo các bài so sánh, cho dùng thương mại với web tĩnh; trang giới hạn của Cloudflare ghi mỗi tệp tối đa 25 MiB. Đây là lựa chọn mình đề xuất. Bạn tự xem lại điều khoản và giới hạn mới nhất trên trang của Cloudflare trước khi dùng, vì chúng có thể thay đổi.
- Hoặc thuê **VPS** rồi dùng Nginx hay Caddy phục vụ thư mục `dist/`.

**Các bước với Cloudflare Pages (giao diện có thể khác đôi chút theo thời gian):**
1. Tạo tài khoản Cloudflare. Vào Workers & Pages, chọn tạo Pages và chọn tải tệp lên trực tiếp (Direct Upload).
2. Đặt tên dự án (ví dụ `sport238`), kéo thả thư mục `dist` (hoặc nội dung giải nén từ `sport238-website.zip`), bấm Deploy.
3. Web chạy ngay ở địa chỉ `sport238.pages.dev`. Hãy thử trên điện thoại.
4. **Tên miền:** mua tên miền ở nhà đăng ký bất kỳ (`.com`, `.vn`...). Trong dự án Pages, chọn Custom domains rồi làm theo hướng dẫn (thường là thêm bản ghi CNAME trỏ về `sport238.pages.dev`). HTTPS được cấp tự động.
5. Điền địa chỉ thật vào `SITE_URL` trong `.env` để khi chia sẻ link lên Facebook hoặc Zalo hiện đúng logo.

## 4. Quy trình hằng ngày

Xem chi tiết: **`HUONG-DAN-CAP-NHAT-HANG-NGAY.md`** (kiểm tra file, sao lưu, báo cáo thay đổi, khôi phục, đặt lịch).

1. Trên Sapo, xuất danh sách sản phẩm ra Excel (nút Xuất file). File nằm trong Tải về là được (công cụ tự chép, không xóa file gốc).
2. Bấm đúp `cap-nhat-web.bat`. Chương trình sẽ: kiểm tra file, sao lưu dữ liệu, nhập vào trang quản trị (ảnh, tên, mô tả, danh mục bạn đã sửa được giữ nguyên), mở báo cáo thay đổi, xuất `dist/` mới, và nếu có `DEPLOY_CMD` thì tự đưa lên hosting.
3. Lỡ nhập nhầm: đóng trang quản trị, bấm `khoi-phuc.bat`.
4. Không có Excel mới mà chỉ vừa thêm ảnh hoặc sửa mô tả: vẫn bấm `cap-nhat-web.bat`, chương trình chỉ xuất lại web.

**Đưa lên hosting tự động:** với Cloudflare, cài công cụ `wrangler` (`npm i -g wrangler`), đăng nhập một lần bằng `wrangler login`, rồi đặt trong `.env`:
`DEPLOY_CMD=npx wrangler pages deploy dist --project-name=sport238`
(Lệnh này mình viết theo hiểu biết, chưa chạy thử với tài khoản của bạn; nếu lỗi, xem hướng dẫn `wrangler pages deploy` của Cloudflare.)

**Chạy theo lịch:** bấm chuột phải `dat-lich.ps1` → Run with PowerShell (mặc định 21:15 mỗi ngày; trang quản trị chưa mở thì tự mở tạm). Máy phải bật.

## 5. Có tự động hóa được việc lấy dữ liệu từ Sapo không?

- Mình **không tìm thấy** tính năng của Sapo POS cho phép tự xuất file Excel theo lịch. Vì vậy bước xuất Excel (khoảng một phút) vẫn do bạn bấm, phần còn lại tự động như trên.
- Để tự động hoàn toàn cần API của Sapo. Bạn nên hỏi Sapo (trong mục Trợ giúp) xem gói và sản phẩm của bạn có hỗ trợ lấy sản phẩm và tồn kho qua API không. Có API thì mình viết lại bước nhập để chạy không cần bạn xuất file.
- Tồn kho trên web là ảnh chụp tại lần nhập gần nhất. Web ghi "Tồn kho cập nhật ngày ..." và "Shop xác nhận còn hàng khi chốt đơn". Nên cập nhật ít nhất mỗi cuối ngày.

## 6. Kiểm tra trước khi mở bán

- [ ] Đổi `ADMIN_PASSWORD`, không dùng `admin123`.
- [ ] Dùng điện thoại thật: chọn size, thêm giỏ, sao chép đơn, mở Zalo, mở Messenger.
- [ ] Bấm thử link Messenger `m.me/Sport238`: cần chắc trang Facebook đã bật nhận tin nhắn.
- [ ] Thêm ảnh cho các sản phẩm chính (trang quản trị lọc sẵn "Chưa có ảnh"). Ảnh tải lên được tự thu nhỏ.
- [ ] Soát danh mục các nhóm Cầu lông, Phụ kiện thể thao. Sản phẩm xếp sai thì chọn lại trong quản trị.
- [ ] Hỏi Sở Công Thương địa phương hoặc Cục Thương mại điện tử và Kinh tế số xem web này có phải thông báo hoặc đăng ký không. Luật Thương mại điện tử 2025 và Nghị định 248/2026/NĐ-CP có hiệu lực từ 1/7/2026 và thay đổi quy định cũ; các nguồn mình đọc chủ yếu nói về sàn và nền tảng, chưa xác nhận được trường hợp web giới thiệu sản phẩm rồi gửi đơn qua chat. Không nên tự kết luận web "không phải thương mại điện tử".
- [ ] Sao lưu thư mục `data` (có `shop.db` và `uploads`) và thư mục `inbox/da-xu-ly` định kỳ ra ổ khác hoặc đám mây.

## 7. Khi nào cần nâng cấp

Web tĩnh hiện tại chỉ có một trang chính (sản phẩm mở bằng `#`), nên Google khó tìm từng sản phẩm. Khi muốn mỗi sản phẩm có địa chỉ riêng để lên Google, hoặc cần đơn hàng, tài khoản khách, tồn kho tức thì, hãy chuyển sang gói `sport-shop-next` (Next.js và Spring Boot) đã chuẩn bị sẵn.
