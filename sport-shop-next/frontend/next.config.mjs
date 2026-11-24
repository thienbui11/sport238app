// API_URL để trống = cách A: đọc data/products.json. Có API_URL = lấy dữ liệu từ backend và dùng được trang /admin.
const api = process.env.API_URL;

/** @type {import('next').NextConfig} */
export default {
  async rewrites() {
    const r = [{ source: "/admin", destination: "/admin/index.html" }];
    if (api) r.push({ source: "/api/:path*", destination: `${api}/api/:path*` }, { source: "/uploads/:path*", destination: `${api}/uploads/:path*` });
    return r;
  },
};
