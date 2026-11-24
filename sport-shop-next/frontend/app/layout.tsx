import type { Metadata, Viewport } from "next";
import Link from "next/link";
import { Be_Vietnam_Pro } from "next/font/google";
import ArtSprite from "@/components/ArtSprite";
import CartDrawer from "@/components/CartDrawer";
import Header, { BottomBar } from "@/components/Header";
import { Icon } from "@/components/Icons";
import Providers from "@/components/Providers";
import { getSite, HOURS, links, phone, SITE_URL } from "@/lib/shop";
import "./globals.css";

// 3 độ đậm là đủ cho hệ thống thiết kế (thường, nhãn/nút, tiêu đề/giá): ít tệp phông hơn, trang nhanh hơn
const font = Be_Vietnam_Pro({ subsets: ["latin", "vietnamese"], weight: ["400", "600", "800"], display: "swap", variable: "--font" });

export const viewport: Viewport = {
  themeColor: [{ media: "(prefers-color-scheme: light)", color: "#ffffff" }, { media: "(prefers-color-scheme: dark)", color: "#1b191b" }],
};

export const metadata: Metadata = {
  icons: { apple: "/icon-192.png" },
  appleWebApp: { capable: true, title: "SPORT 238", statusBarStyle: "default" },
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
        <ArtSprite />
        <Providers site={site}>
          <Header />
          <main>{children}</main>
          <footer>
            <div className="wrap">
              <div>
                <p className="fb"><img src="/logo-96.webp" alt="" width={40} height={40} loading="lazy" />{site.name} – KCN AN HIỆP</p>
                <p>Đồ bóng đá, giày, quần áo thể thao, phụ kiện. Chọn hàng trên web, nhắn shop qua Zalo hoặc Messenger, rồi ghé shop nhận hàng.</p>
              </div>
              <ul>
                <li><Icon n="pin" /><span id="fad">{site.address}</span></li>
                <li><Icon n="clock" /><span id="fhr">Mở cửa {HOURS.time}, {HOURS.days}</span></li>
                <li><Icon n="chat" /><span>Zalo <a id="fz" href={l.zalo} target="_blank" rel="noopener">{phone(site.zalo)}</a> · <a id="ff" href={l.page} target="_blank" rel="noopener">Facebook</a></span></li>
              </ul>
              <p className="flinks"><Link href="/bang-size/">Bảng size</Link> · <Link href="/dat-doi/">Đặt đồng phục đội</Link> · <Link href="/#cach-mua">Cách mua</Link> · <Link href="/#ve-shop">Về shop</Link></p>
              <p className="fnote">© {site.name}. Tồn kho cập nhật theo đợt, shop xác nhận còn hàng khi chốt đơn.</p>
            </div>
          </footer>
          <BottomBar />
          {/* Nút Zalo nổi: giữ lại cho tương thích, nhưng không hiện (đầu trang đã có nút Zalo dính, điện thoại có thanh dưới) */}
          <a className="fab" id="fab" href={l.zalo} target="_blank" rel="noopener" aria-label="Nhắn Zalo cho shop"><Icon n="chat" /></a>
          <CartDrawer />
        </Providers>
      </body>
    </html>
  );
}
