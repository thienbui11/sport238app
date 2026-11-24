import Link from "next/link";

export const metadata = { title: "Không tìm thấy trang | SPORT 238" };

export default function NotFound() {
  return (
    <div className="wrap nf">
      <h1>Không tìm thấy trang này</h1>
      <p>Có thể sản phẩm đã ngừng bán hoặc đường dẫn bị sai.</p>
      <Link className="btn" href="/#san-pham">Xem sản phẩm đang bán</Link>
    </div>
  );
}
