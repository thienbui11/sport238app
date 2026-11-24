import type { Metadata } from "next";
import { Be_Vietnam_Pro } from "next/font/google";
import CartDrawer from "@/components/CartDrawer";
import Header, { BottomBar } from "@/components/Header";
import Providers from "@/components/Providers";
import { getSite, HOURS, links, phone, SITE_URL } from "@/lib/shop";
import "./globals.css";

const font = Be_Vietnam_Pro({ subsets: ["latin", "vietnamese"], weight: ["400", "500", "600", "700", "800"], variable: "--font" });

export const metadata: Metadata = {
  ...(SITE_URL ? { metadataBase: new URL(SITE_URL), alternates: { canonical: "/" } } : {}),
  openGraph: { type: "website", locale: "vi_VN", siteName: "SPORT 238", title: "SPORT 238 – Đồ bóng đá, giày, phụ kiện", description: "Chọn size, thêm vào giỏ rồi nhắn shop qua Zalo hoặc Messenger. Ghé shop nhận hàng tại KCN An Hiệp, Vĩnh Long.", ...(SITE_URL ? { url: "/", images: [{ url: "/logo.png", alt: "SPORT 238" }] } : {}) },
  title: "SPORT 238 – Đồ bóng đá, giày, phụ kiện | KCN An Hiệp",
  description: "SPORT 238 – KCN An Hiệp, Vĩnh Long: áo bóng đá, giày bóng đá, quần áo thể thao, đồng phục đội nhóm, phụ kiện bóng đá. Mở cửa 8:00–21:00 hằng ngày.",
};

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const site = await getSite();
  const l = links(site);
  return (
    <html lang="vi" className={font.variable}>
      <body>
        <Providers site={site}>
          <Header />
          <main>{children}</main>
          <footer><div className="wrap">
            <b>{site.name} – KCN AN HIỆP</b><br />
            <span id="fad">📍 {site.address}</span><br />
            <span id="fhr">🕗 Mở cửa {HOURS.time}, {HOURS.days}</span><br />
            Zalo <a id="fz" href={l.zalo} target="_blank" rel="noopener">{phone(site.zalo)}</a> · <a id="ff" href={l.page} target="_blank" rel="noopener">Facebook</a><br />
            © {site.name}. Tồn kho cập nhật theo đợt, shop xác nhận còn hàng khi chốt đơn.
          </div></footer>
          <BottomBar />
          <a className="fab" id="fab" href={l.zalo} target="_blank" rel="noopener" aria-label="Nhắn Zalo cho shop">💬</a>
          <CartDrawer />
        </Providers>
      </body>
    </html>
  );
}
