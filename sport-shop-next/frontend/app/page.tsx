import Storefront from "@/components/Shop";
import { CATEGORIES, getCatalog, getSite, HOURS, links, phone } from "@/lib/shop";

export const revalidate = 60;

const RIBBON = ["ÁO CLB & ĐỘI TUYỂN ⚽", "GIÀY BÓNG ĐÁ 👟", "ĐỒNG PHỤC ĐỘI NHÓM 🎽", "CÚP · HUY CHƯƠNG 🏆", "PHỤ KIỆN 🎒", "CẦU LÔNG 🏸"];
const SERVICES = ["Áo bóng đá CLB và đội tuyển", "Áo bóng đá không logo", "Giày bóng đá, giày thể dục", "Quần áo thể thao", "Đồng phục đội nhóm, công ty", "Phụ kiện bóng đá, thể thao"];

export default async function Home() {
  const [{ products, updated }, site] = await Promise.all([getCatalog(), getSite()]);
  const l = links(site);
  return (
    <>
      <div className="herobg">
        <div className="wrap">
          <section id="top" className="hero">
            <div>
              <span className="pill">⚽ PASSION FOR FOOTBALL</span>
              <h1>Đồ bóng đá,<br /><span className="hl">chọn đúng size</span><br />nhận tại shop</h1>
              <p>Xem size, màu và tình trạng hàng, thêm vào giỏ rồi gửi danh sách cho shop qua Zalo hoặc Messenger. Shop giữ hàng, bạn ghé lấy.</p>
              <div className="hbtns">
                <a className="btn" href="#san-pham">Xem sản phẩm →</a>
                <a className="btn ghost" data-zl href={l.zalo} target="_blank" rel="noopener">💬 Nhắn Zalo</a>
              </div>
            </div>
            <div className="art" aria-hidden="true">
              <div className="b2" /><div className="b1" /><img className="lg" src="/logo.png" alt="" />
              <span className="e1">⚽</span><span className="e2">👟</span><span className="e3">🏆</span>
              <span className="cf f1">👟 Giày bóng đá</span><span className="cf f2">🏆 Cúp · Huy chương</span><span className="cf f3">⚽ Áo CLB &amp; đội tuyển</span>
            </div>
          </section>
          <div className="stats">
            <div className="stat"><b>{products.length}</b><span>sản phẩm</span></div>
            <div className="stat"><b>{CATEGORIES.length}</b><span>danh mục</span></div>
            <div className="stat"><b>📏</b><span>Xem tồn từng size</span></div>
            <div className="stat"><b>📍</b><span>Ghé shop nhận hàng</span></div>
          </div>
        </div>
      </div>
      <div className="ribbon" aria-hidden="true"><div>{[...RIBBON, ...RIBBON].map((t, i) => <span key={i}>{t}</span>)}</div></div>

      <Storefront products={products} updated={updated} />

      <section id="ve-shop" className="sec wrap">
        <div className="about">
          <h2>Về {site.name}</h2>
          <p>{site.name} – KCN An Hiệp chuyên cung cấp quần áo, giày, phụ kiện bóng đá, cầu lông… Nhắn shop để được tư vấn size và giữ hàng, sau đó ghé shop nhận hàng.</p>
          <div className="tags">{SERVICES.map((s) => <span key={s}>{s}</span>)}</div>
          <p className="addr2">📍 {site.address}</p>
          <p className="hours">🕗 Mở cửa {HOURS.time}, {HOURS.days}</p>
          <div className="links"><a data-map href={l.map} target="_blank" rel="noopener">Chỉ đường</a><a data-fp href={l.page} target="_blank" rel="noopener">Facebook</a><a data-zl href={l.zalo} target="_blank" rel="noopener">Zalo {phone(site.zalo)}</a></div>
        </div>
      </section>
      <section id="cach-mua" className="sec wrap">
        <span className="eyebrow">CÁCH MUA</span>
        <h2>Mua hàng siêu dễ</h2><p className="sub" />
        <div className="steps">
          <div className="step"><i>1</i><b>Chọn món</b><span>Chọn size, màu rồi thêm vào giỏ</span></div>
          <div className="step"><i>2</i><b>Nhắn shop</b><span>Gửi danh sách qua Zalo hoặc Messenger</span></div>
          <div className="step"><i>3</i><b>Ghé shop nhận hàng</b><span>Shop giữ hàng cho bạn, bạn ghé lấy tại cửa hàng (mở cửa {HOURS.time} hằng ngày)</span></div>
        </div>
        <div className="cta"><a className="btn" data-zl href={l.zalo} target="_blank" rel="noopener">💬 Nhắn Zalo {phone(site.zalo)}</a><a className="btn ghost" data-fb href={l.messenger} target="_blank" rel="noopener">Nhắn Messenger</a></div>
      </section>
    </>
  );
}
