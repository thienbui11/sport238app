// Hai cách chạy:
// 1) Xuất WEB TĨNH (XUAT_TINH=1, dùng cho cửa hàng thật): mỗi sản phẩm một trang HTML riêng trong thư mục out/,
//    dữ liệu lấy lúc build từ trang quản trị (API_URL). Chạy bằng sport-shop-app/tools/export_next.py.
// 2) Máy chủ Next (next start): API_URL để trống = đọc data/products.json; có API_URL = lấy dữ liệu từ backend và dùng được /admin.
const api = process.env.API_URL;
const tinh = process.env.XUAT_TINH === "1";

/** @type {import('next').NextConfig} */
export default tinh
  ? { output: "export", trailingSlash: true, images: { unoptimized: true } }
  : {
      async rewrites() {
        const r = [{ source: "/admin", destination: "/admin/index.html" }];
        if (api) r.push({ source: "/api/:path*", destination: `${api}/api/:path*` }, { source: "/uploads/:path*", destination: `${api}/uploads/:path*` });
        return r;
      },
    };
