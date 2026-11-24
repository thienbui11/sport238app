import type { MetadataRoute } from "next";
import { SLOGAN } from "@/lib/shop";

export const dynamic = "force-static";

/** C3: cài web như ứng dụng trên điện thoại ("Thêm vào màn hình chính") */
export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "SPORT 238 – KCN An Hiệp",
    short_name: "SPORT 238",
    description: `${SLOGAN} Ghé shop nhận hàng tại KCN An Hiệp, Vĩnh Long.`,
    lang: "vi",
    start_url: "/",
    scope: "/",
    display: "standalone",
    background_color: "#f5f3f3",
    theme_color: "#a3122a",
    icons: [
      { src: "/icon-192.png", sizes: "192x192", type: "image/png", purpose: "any" },
      { src: "/icon-512.png", sizes: "512x512", type: "image/png", purpose: "any" },
      { src: "/icon-maskable-512.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
    ],
  };
}
