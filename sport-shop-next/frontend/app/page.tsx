import { Icon } from "@/components/Icons";
import Storefront from "@/components/Shop";
import { abs, CATEGORIES, getCatalog, getSite, HOURS, links, pack, phone, SITE_URL } from "@/lib/shop";

export const revalidate = 60;

const SERVICES = ["Áo bóng đá CLB và đội tuyển", "Áo bóng đá không logo", "Giày bóng đá, giày thể thao", "Quần áo thể thao trẻ em", "Đồng phục đội nhóm, công ty", "Phụ kiện bóng đá, cầu lông"];

export default async function Home() {
  const [{ products, updated }, site] = await Promise.all([getCatalog(), getSite()]);
  const l = links(site);
  // Thông tin cửa hàng cho Google (địa chỉ, giờ mở cửa). Không ghi số điện thoại khi chủ shop chưa xác nhận số gọi được.
  const ld = {
    "@context": "https://schema.org", "@type": "SportingGoodsStore", name: site.name,
    address: { "@type": "PostalAddress", streetAddress: "238 ấp Thuận Điền (Ngã 3 KCN An Hiệp)", addressLocality: "xã Phú Túc", addressRegion: "Vĩnh Long", addressCountry: "VN" },
    openingHoursSpecification: [{ "@type": "OpeningHoursSpecification", dayOfWeek: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], opens: "08:00", closes: "21:00" }],
    sameAs: [l.page],
    ...(SITE_URL ? { url: abs("/"), image: abs("/logo.png") } : {}),
  };
  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(ld).replace(/</g, "\\u003c") }} />
      <section id="top" className="hero" aria-labelledby="hero-h">
        <div className="wrap">
          <div>
            <span className="kick">Shop bóng đá · KCN An Hiệp</span>
            <h1 id="hero-h">Chọn size, nhắn Zalo, <em>ghé shop nhận hàng</em></h1>
            <p className="lead">Áo CLB, áo không logo, giày bóng đá, vớ và phụ kiện. Xem tồn kho từng size, gửi đơn qua Zalo hoặc Messenger, shop giữ hàng cho bạn.</p>
            <div className="hbtns">
              <a className="btn" href="#san-pham">Xem sản phẩm<Icon n="arrow" /></a>
              <a className="btn light" data-zl href={l.zalo} target="_blank" rel="noopener"><Icon n="chat" />Nhắn Zalo</a>
            </div>
            <div className="stats">
              <div className="stat"><b>{products.length}</b><span>sản phẩm</span></div>
              <div className="stat"><b>{CATEGORIES.length}</b><span>danh mục</span></div>
              <div className="stat"><b>{HOURS.time}</b><span>mở cửa mỗi ngày</span></div>
            </div>
          </div>
          <aside className="visit" aria-label="Địa chỉ cửa hàng">
            <div className="vt"><img src="/logo-96.webp" alt="" width={48} height={48} /><div><b>Ghé shop nhận hàng</b><span>{site.name} – KCN An Hiệp</span></div></div>
            <ul>
              <li><Icon n="pin" /><span>{site.address}</span></li>
              <li><Icon n="clock" /><span>Mở cửa {HOURS.time}, {HOURS.days}</span></li>
            </ul>
            <div className="row">
              <a className="btn ghost sm" data-map href={l.map} target="_blank" rel="noopener"><Icon n="map" />Chỉ đường</a>
              <a className="btn sm" data-zl href={l.zalo} target="_blank" rel="noopener"><Icon n="chat" />Zalo</a>
            </div>
          </aside>
        </div>
      </section>
      <div className="perks">
        <ul className="wrap">
          <li><span className="pi"><Icon n="ruler" /></span><span><b>Xem tồn từng size</b><small>Biết size nào còn trước khi nhắn</small></span></li>
          <li><span className="pi"><Icon n="box" /></span><span><b>Giữ hàng cho bạn</b><small>Nhắn Zalo, shop xác nhận và giữ hàng</small></span></li>
          <li><span className="pi"><Icon n="store" /></span><span><b>Ghé shop nhận</b><small>Ngã 3 KCN An Hiệp, mở cửa mỗi ngày</small></span></li>
        </ul>
      </div>

      <Storefront data={pack(products)} updated={updated} />

      <section id="ve-shop" className="sec wrap" aria-labelledby="vs-h">
        <div className="sh"><div><h2 id="vs-h">Về {site.name}</h2></div></div>
        <div className="about">
          <div className="panel">
            <p>{site.name} – KCN An Hiệp chuyên quần áo, giày, phụ kiện bóng đá và cầu lông. Nhắn shop để được tư vấn size và giữ hàng, sau đó ghé shop nhận hàng.</p>
            <div className="tags">{SERVICES.map((s) => <span key={s}>{s}</span>)}</div>
          </div>
          <div className="panel">
            <ul className="info">
              <li><Icon n="pin" /><span className="addr2">{site.address}</span></li>
              <li><Icon n="clock" /><span className="hours">Mở cửa {HOURS.time}, {HOURS.days}</span></li>
            </ul>
            <div className="links">
              <a className="btn ghost sm" data-map href={l.map} target="_blank" rel="noopener"><Icon n="map" />Chỉ đường</a>
              <a className="btn ghost sm" data-fp href={l.page} target="_blank" rel="noopener"><Icon n="facebook" />Facebook</a>
              <a className="btn sm" data-zl href={l.zalo} target="_blank" rel="noopener"><Icon n="chat" />Zalo {phone(site.zalo)}</a>
            </div>
          </div>
        </div>
      </section>

      <section id="cach-mua" className="sec wrap" aria-labelledby="cm-h">
        <div className="sh"><div><h2 id="cm-h">Cách mua hàng</h2><p className="sub">Không cần tài khoản, không thanh toán trên web.</p></div></div>
        <ol className="steps">
          <li className="step"><i>1</i><div><b>Chọn món</b><p>Chọn size, màu rồi bấm “Thêm vào giỏ”.</p></div></li>
          <li className="step"><i>2</i><div><b>Nhắn shop</b><p>Mở giỏ, bấm gửi đơn qua Zalo hoặc Messenger.</p></div></li>
          <li className="step"><i>3</i><div><b>Ghé shop nhận hàng</b><p>Shop giữ hàng cho bạn. Mở cửa {HOURS.time} hằng ngày.</p></div></li>
        </ol>
        <div className="cta">
          <a className="btn" data-zl href={l.zalo} target="_blank" rel="noopener"><Icon n="chat" />Nhắn Zalo {phone(site.zalo)}</a>
          <a className="btn ghost" data-fb href={l.messenger} target="_blank" rel="noopener"><Icon n="messenger" />Nhắn Messenger</a>
        </div>
      </section>
    </>
  );
}
