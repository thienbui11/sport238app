import Link from "next/link";

export const metadata = { title: "Không tìm thấy trang | SPORT 238" };

export default function NotFound() {
  return (
    <div className="wrap" style={{ textAlign: "center", padding: "64px 16px" }}>
      <h1 style={{ fontSize: 30, margin: "0 0 10px" }}>Không tìm thấy trang này</h1>
      <p style={{ color: "var(--muted)", margin: "0 0 22px" }}>Có thể sản phẩm đã ngừng bán hoặc đường dẫn bị sai.</p>
      <Link className="btn" href="/#san-pham">Xem sản phẩm đang bán</Link>
    </div>
  );
}
