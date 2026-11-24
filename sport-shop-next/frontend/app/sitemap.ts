import type { MetadataRoute } from "next";
import { abs, getCatalog, SITE_URL } from "@/lib/shop";

export const dynamic = "force-static";

/** sitemap.xml cho Google: trang chủ + từng sản phẩm. Cần SITE_URL (địa chỉ web thật); chưa có thì để trống. */
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  if (!SITE_URL) return [];
  const { products } = await getCatalog();
  return [{ url: abs("/"), changeFrequency: "daily", priority: 1 },
    ...products.map((p) => ({ url: abs(`/san-pham/${encodeURIComponent(p.id)}/`), changeFrequency: "daily" as const, priority: 0.7 }))];
}
