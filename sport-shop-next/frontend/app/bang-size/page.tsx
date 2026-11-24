import type { Metadata } from "next";
import Link from "next/link";
import { Icon } from "@/components/Icons";
import { SizeFinder, SizeTable } from "@/components/SizeGuide";
import { SITE_URL } from "@/lib/shop";
import { BRANDS } from "@/lib/sizes";

export const metadata: Metadata = {
  title: "Bảng size áo bóng đá theo hãng | SPORT 238",
  description: "Bảng size áo bóng đá RIKI, WIN, Strivend, Bulbal, AMAC, Just Play, Sao Việt, Kaiwin, Egan và gợi ý size theo chiều cao, cân nặng. Ghé shop nhận hàng tại KCN An Hiệp, Vĩnh Long.",
  ...(SITE_URL ? { alternates: { canonical: "/bang-size/" } } : {}),
};

export default function Page() {
  return (
    <div className="wrap sizepage">
      <Link className="back" href="/#san-pham"><Icon n="left" />Tất cả sản phẩm</Link>
      <h1>Bảng size áo bóng đá</h1>
      <p className="lead2">Số đo do hãng cung cấp, mang tính tham khảo. Nhập chiều cao, cân nặng để xem size gợi ý; phân vân thì nhắn shop để được tư vấn. Giày chưa có bảng size: bạn chọn theo size giày đang mang.</p>
      <SizeFinder />
      <nav className="chips brandnav" aria-label="Chọn hãng">
        {BRANDS.map((b) => <a key={b.id} className="chip" href={`#${b.id}`}>{b.ten}</a>)}
      </nav>
      {BRANDS.map((b) => (
        <section key={b.id} id={b.id} className="brandsec" aria-labelledby={`${b.id}-h`}>
          <h2 id={`${b.id}-h`}>{b.ten}</h2>
          {b.bang.map((c) => <SizeTable key={c.nguon + c.tieu_de} b={b} c={c} />)}
        </section>
      ))}
      <p className="muted">Hãng khác (CV, HD Sport, Wika, Mira, Peace Max…): chưa có bảng size, nhắn shop để được tư vấn.</p>
    </div>
  );
}
