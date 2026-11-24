# Đưa web SPORT 238 lên mạng

Dành cho chủ shop. Các việc có đăng ký tài khoản, mua tên miền, đưa web lên mạng là **anh/chị tự làm** (hoặc nhờ người tin cậy); công cụ trong máy chỉ chuẩn bị sẵn.
Thông tin về Cloudflare dưới đây tra ngày 24/11/2026; điều khoản có thể đổi, nên xem lại trang gốc (link ở mỗi mục) trước khi dùng.

## 1. Cách hoạt động

- **Web khách xem** là một thư mục tĩnh `dist/` (trang HTML, ảnh, `products.json`). Mỗi sản phẩm có một trang riêng `/san-pham/<MÃ>/` để Google, Zalo, Facebook hiện đúng tên, ảnh, giá. Không có máy chủ, không có cơ sở dữ liệu trên mạng: rẻ, nhanh, ít hỏng.
- **Trang quản trị** chạy trên máy tính ở shop (`chay-quan-tri.bat`, địa chỉ http://localhost:3000/admin). **Không đưa trang quản trị lên mạng.** Khi xuất web, trang quản trị tự bị loại khỏi `dist/`.
- Mỗi ngày bấm `cap-nhat-web.bat`: nhập file Excel Sapo, xuất `dist/` mới, và (nếu đã cài ở mục 5) tự đưa lên mạng. Xem `HUONG-DAN-CAP-NHAT-HANG-NGAY.md`.

## 2. Cài trên máy shop (một lần)

1. Cài **Node.js 22.9 trở lên** (nodejs.org) và **Python 3.10 trở lên** (python.org, nhớ tích "Add to PATH").
2. Mở dòng lệnh trong thư mục dự án, chạy:
   - `pip install pandas openpyxl pillow`
   - `cd sport-shop-next\frontend` rồi `npm install` (để xuất web bản chính; chưa cài thì công cụ tự dùng bản HTML dự phòng).
3. Trong thư mục `sport-shop-app`, chép `.env.example` thành **`.env`** rồi sửa:
   - `ADMIN_PASSWORD=` mật khẩu mạnh (không dùng `admin123`). Tệp `.env` không được đưa lên git hay lên mạng.
   - `SITE_URL=` địa chỉ web thật (điền sau khi có, ví dụ `https://sport238.vn`).
4. Bấm đúp `chay-quan-tri.bat`, mở http://localhost:3000/admin để kiểm tra.

## 3. Chọn nơi đặt web: Cloudflare Pages (gói miễn phí)

| Mục | Gói miễn phí | Web SPORT 238 hiện tại |
|---|---|---|
| Số tệp mỗi web | 20.000 | ~935 tệp (chưa có ảnh); mỗi ảnh thêm 1 tệp |
| Dung lượng mỗi tệp | 25 MiB | ảnh đã thu nhỏ còn vài trăm KB |
| Tên miền riêng | 100 mỗi dự án | 1 |
| Băng thông trang tĩnh | trang giới hạn không ghi giới hạn | — |

Nguồn: [Cloudflare Pages – Limits](https://developers.cloudflare.com/pages/platform/limits/).

- Điều khoản dịch vụ cho nền tảng (Workers/Pages) mình đọc **không có câu cấm dùng thương mại ở gói miễn phí**; có ghi Cloudflare có thể tạm giới hạn lưu trữ/lượt truy cập nếu gây quá tải, và có thể đổi tên miền phụ `*.pages.dev` (thường báo trước ít nhất một tuần; không áp dụng cho tên miền riêng). Nguồn: [Cloudflare Service-Specific Terms – Developer Platform](https://www.cloudflare.com/service-specific-terms-developer-platform/). Vì vậy **nên dùng tên miền riêng**.
- **Không dùng Vercel gói miễn phí (Hobby)**: điều khoản chỉ cho dùng cá nhân, phi thương mại; web giới thiệu hàng để bán thuộc diện thương mại (phải dùng gói Pro, có phí).
- **Không dùng GitHub Pages** cho web bán hàng.

## 4. Đưa lên lần đầu (làm một lần, khoảng 15 phút)

> Kéo thả thư mục trên trang Cloudflare chỉ nhận tối đa **1.000 tệp**, web đã ~935 tệp và sẽ tăng khi thêm ảnh. Vì vậy dùng lệnh `wrangler` (tối đa 20.000 tệp). Nguồn: [Direct Upload](https://developers.cloudflare.com/pages/get-started/direct-upload/).

1. Tạo tài khoản Cloudflare (miễn phí) tại cloudflare.com.
2. Bấm `cap-nhat-web.bat` để có thư mục `sport-shop-app\dist` mới nhất.
3. Mở dòng lệnh trong thư mục `sport-shop-app`, chạy lần lượt:
   ```
   npx wrangler login
   npx wrangler pages project create sport238 --production-branch=main
   npx wrangler pages deploy dist --project-name=sport238 --branch=main
   ```
   - `wrangler login` mở trình duyệt để anh/chị đăng nhập Cloudflare và bấm cho phép (chỉ một lần trên máy này).
   - Tên dự án `sport238` đã có người dùng thì đổi tên khác, và dùng đúng tên đó ở các lệnh sau.
   - Luôn ghi `--branch=main` (trùng nhánh chính đã tạo). Thiếu nó, máy đang dùng git ở nhánh khác thì web chỉ lên **bản xem thử**, không phải web chính.
4. Mở địa chỉ `https://sport238.pages.dev` (hoặc tên dự án của anh/chị) trên **điện thoại thật**: chọn size, thêm giỏ, sao chép đơn, mở Zalo, mở Messenger.

## 5. Tự đưa lên mỗi lần cập nhật

Thêm vào tệp `.env`:
```
DEPLOY_CMD=npx wrangler pages deploy dist --project-name=sport238 --branch=main
```
Từ đó mỗi lần bấm `cap-nhat-web.bat` (hoặc máy tự chạy theo lịch `dat-lich.ps1`), web mới tự lên mạng. Kết quả ghi trong `daily_update.log` ("Đưa lên hosting thành công" / "THẤT BẠI").

Không muốn dùng `wrangler login` (ví dụ máy chạy theo lịch không đăng nhập được): tạo **API token** trong Cloudflare (Custom Token, quyền *Account → Cloudflare Pages → Edit*), lấy **Account ID** (trang tổng quan, mục API bên phải), rồi điền vào `.env`:
```
CLOUDFLARE_API_TOKEN=...
CLOUDFLARE_ACCOUNT_ID=...
```
Nguồn: [Use Direct Upload with continuous integration](https://developers.cloudflare.com/pages/how-to/use-direct-upload-with-continuous-integration/). Khóa này như mật khẩu: chỉ để trong `.env`, không gửi cho ai.

## 6. Tên miền riêng và HTTPS

1. Mua tên miền ở nhà đăng ký bất kỳ (`.vn`, `.com.vn`, `.com`…).
2. Trong Cloudflare: Workers & Pages → dự án `sport238` → **Custom domains** → thêm tên miền, làm theo hướng dẫn (thường là thêm bản ghi CNAME trỏ về `sport238.pages.dev`, hoặc chuyển tên miền sang Cloudflare quản lý). **HTTPS được cấp tự động.**
3. Điền `SITE_URL=https://ten-mien-cua-shop` vào `.env`, bấm lại `cap-nhat-web.bat`: sơ đồ web (`sitemap.xml`), ảnh chia sẻ Zalo/Facebook, dữ liệu cho Google sẽ dùng đúng địa chỉ.
4. Khai báo với Google: vào Google Search Console, thêm tên miền, gửi `https://ten-mien-cua-shop/sitemap.xml`.

## 7. Xem số người ghé web (không cookie)

Cloudflare **Web Analytics** miễn phí, không dùng cookie hay localStorage để đếm. Nguồn: [Cloudflare Web Analytics](https://www.cloudflare.com/web-analytics/).
Bật: Workers & Pages → dự án → **Metrics** → Web Analytics → **Enable**, rồi đưa web lên lại một lần (bấm `cap-nhat-web.bat`). Nguồn: [Get started](https://developers.cloudflare.com/web-analytics/get-started/).

## 8. Kiểm tra trước khi mở bán

- [ ] `.env` có `ADMIN_PASSWORD` mạnh; trang quản trị **không** mở ra mạng (chỉ dùng ở máy shop).
- [ ] Điện thoại thật: chọn size, thêm giỏ, sao chép đơn, mở Zalo, mở Messenger, "Gửi đơn kèm ảnh" (khi đã có ảnh).
- [ ] Bấm thử link Messenger `m.me/Sport238`: trang Facebook đã bật nhận tin nhắn.
- [ ] Thêm ảnh cho các sản phẩm chính (`nap-anh.bat`; trang quản trị lọc "Chưa có ảnh" + "Tồn nhiều trước").
- [ ] Soát danh mục; sản phẩm xếp sai thì chọn lại trong trang quản trị (sửa hàng loạt được).
- [ ] **Hỏi Sở Công Thương** (hoặc Cục Thương mại điện tử và Kinh tế số) xem web này có phải **thông báo/đăng ký** không. Luật Thương mại điện tử 2025 và Nghị định 248/2026/NĐ-CP có hiệu lực từ 1/7/2026; các nguồn mình đọc chủ yếu nói về sàn và nền tảng, chưa xác nhận được trường hợp web giới thiệu sản phẩm rồi gửi đơn qua chat. Không tự kết luận web "không phải thương mại điện tử".
- [ ] Sao lưu định kỳ ra ổ khác hoặc đám mây: thư mục `sport-shop-app\data` (có `shop.db`, `uploads`, `sao-luu`) và thư mục ảnh gốc.

## 9. Khi cần thêm

Cần đơn hàng, tài khoản khách, tồn kho tức thời (không qua Excel) thì dùng backend `sport-shop-next/backend` (Spring Boot + PostgreSQL) đã chuẩn bị sẵn nhưng **chưa chạy thật**; khi đó cần máy chủ có phí và API của Sapo (xem `HUONG-DAN-CAP-NHAT-HANG-NGAY.md`).
