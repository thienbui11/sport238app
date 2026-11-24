import type { Metadata } from "next";
import Link from "next/link";
import { Icon } from "@/components/Icons";
import TeamOrder from "@/components/TeamOrder";
import { getCatalog, SITE_URL } from "@/lib/shop";

export const metadata: Metadata = {
  title: "Đặt đồng phục đội bóng, in tên số | SPORT 238",
  description: "Chọn mẫu áo, số lượng theo size, danh sách in tên và số áo, rồi gửi đơn cho shop qua Zalo. In tên + số từ 5 bộ 15.000đ/bộ, từ 10 bộ 10.000đ/bộ. Ghé shop nhận hàng tại KCN An Hiệp, Vĩnh Long.",
  ...(SITE_URL ? { alternates: { canonical: "/dat-doi/" } } : {}),
};

export default async function Page() {
  const { products } = await getCatalog();
  const kits = products.filter((p) => ["Quần áo không logo", "Quần áo CLB/Đội tuyển", "Quần áo trẻ em"].includes(p.cat))
    .sort((a, b) => Number(b.stock > 0) - Number(a.stock > 0) || a.name.localeCompare(b.name, "vi"));
  return (
    <div className="wrap sizepage">
      <Link className="back" href="/#san-pham"><Icon n="left" />Tất cả sản phẩm</Link>
      <h1>Đặt đồng phục đội</h1>
      <p className="lead2">Chọn mẫu áo, số lượng theo size và danh sách in tên, số áo. Web tạo sẵn tin nhắn đầy đủ để bạn gửi cho shop qua Zalo hoặc Messenger; shop xác nhận và báo thời gian, bạn ghé shop nhận hàng.</p>
      <TeamOrder products={kits} />
    </div>
  );
}
