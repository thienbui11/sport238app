import type { Metadata } from "next";
import { Be_Vietnam_Pro } from "next/font/google";
import CartDrawer from "@/components/CartDrawer";
import Header from "@/components/Header";
import Providers from "@/components/Providers";
import { getSite, links, phone } from "@/lib/shop";
import "./globals.css";

const font = Be_Vietnam_Pro({ subsets: ["latin", "vietnamese"], weight: ["400", "500", "600", "700", "800"], variable: "--font" });

export const metadata: Metadata = {
  title: "SPORT 238 – Đồ bóng đá, giày, phụ kiện | KCN An Hiệp",
  description: "SPORT 238 – KCN An Hiệp, Vĩnh Long: áo bóng đá, giày bóng đá, quần áo thể thao, đồng phục đội nhóm, phụ kiện bóng đá.",
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
            Zalo <a id="fz" href={l.zalo} target="_blank" rel="noopener">{phone(site.zalo)}</a> · <a id="ff" href={l.page} target="_blank" rel="noopener">Facebook</a><br />
            © {site.name}. Tồn kho cập nhật theo đợt, shop xác nhận còn hàng khi chốt đơn.
          </div></footer>
          <a className="fab" id="fab" href={l.zalo} target="_blank" rel="noopener" aria-label="Nhắn Zalo cho shop">💬</a>
          <CartDrawer />
        </Providers>
      </body>
    </html>
  );
}
