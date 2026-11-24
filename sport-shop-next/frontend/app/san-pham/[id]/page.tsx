import type { Metadata } from "next";
import { notFound } from "next/navigation";
import ProductDetail from "@/components/ProductDetail";
import { abs, defaultColor, getCatalog, imgsFor, money, priceText, SITE_URL, type Product } from "@/lib/shop";

export const revalidate = 60;

export async function generateStaticParams() {
  const { products } = await getCatalog();
  return products.map((p) => ({ id: p.id }));
}

type Props = { params: Promise<{ id: string }> };

async function find(id: string) {
  const { products, updated } = await getCatalog();
  const p = products.find((x) => x.id === decodeURIComponent(id));
  // B4: sản phẩm cùng loại (cùng danh mục; ưu tiên cùng hãng, còn hàng), tính sẵn lúc xuất web
  const related = !p ? [] : products.filter((x) => x.id !== p.id && x.cat === p.cat)
    .sort((a, b) => Number(b.stock > 0) - Number(a.stock > 0) || Number(!!p.brand && b.brand === p.brand) - Number(!!p.brand && a.brand === p.brand))
    .slice(0, 8).map((x) => ({ id: x.id, name: x.name, cat: x.cat, price: priceText(x), color: defaultColor(x), img: imgsFor(x, defaultColor(x))[0] }));
  // Sapo có vài sản phẩm trùng tên: thêm mã để mỗi trang có tiêu đề riêng (chủ shop nên đặt "Tên hiển thị" khác nhau)
  const dup = !!p && products.some((x) => x !== p && x.name === p.name);
  return { p, updated, related, label: p ? (dup ? `${p.name} (mã ${p.id})` : p.name) : "" };
}

const priceRange = (p: Product) => (p.min === p.max ? money(p.min) : `${money(p.min)} – ${money(p.max)}`);
const firstImage = (p: Product) => imgsFor(p, defaultColor(p))[0] ?? Object.values(p.images).flat()[0];

/** Mô tả ngắn cho Google và khi chia sẻ Zalo/Facebook: chỉ dùng dữ liệu thật của sản phẩm */
function describe(p: Product, label = p.name) {
  const sizes = p.sizes.filter(Boolean);
  return [
    `${label}, danh mục ${p.cat}${p.brand ? `, hãng ${p.brand}` : ""}.`,
    `Giá ${priceRange(p)}.`,
    sizes.length ? `Size ${sizes.join(", ")}.` : "",
    p.stock > 0 ? "Còn hàng." : "Tạm hết hàng.",
    "Chọn size, nhắn shop qua Zalo, ghé shop nhận hàng tại KCN An Hiệp, Vĩnh Long.",
  ].filter(Boolean).join(" ");
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  const { p, label } = await find(id);
  if (!p) return { title: "Không tìm thấy sản phẩm | SPORT 238" };
  const title = `${label} | SPORT 238`, description = describe(p, label), path = `/san-pham/${encodeURIComponent(p.id)}/`;
  const img = firstImage(p) ?? "/logo.png";
  return {
    title, description,
    ...(SITE_URL ? { alternates: { canonical: path } } : {}),
    openGraph: { title, description, type: "website", locale: "vi_VN", siteName: "SPORT 238", ...(SITE_URL ? { url: path, images: [{ url: img, alt: p.name }] } : {}) },
    twitter: { card: SITE_URL ? "summary_large_image" : "summary", title, description },
  };
}

export default async function Page({ params }: Props) {
  const { id } = await params;
  const { p, updated, related } = await find(id);
  if (!p) notFound();
  const img = firstImage(p);
  // Dữ liệu cấu trúc cho Google: chỉ giá, tình trạng, hãng thật — không ghi đánh giá, bảo hành, "chính hãng"
  const ld = {
    "@context": "https://schema.org", "@type": "Product", name: p.name, sku: p.variants[0]?.sku, category: p.cat,
    description: describe(p),
    ...(p.brand ? { brand: { "@type": "Brand", name: p.brand } } : {}),
    ...(img && SITE_URL ? { image: img.startsWith("http") ? img : abs(img) } : {}),
    offers: {
      "@type": "AggregateOffer", priceCurrency: "VND", lowPrice: p.min, highPrice: p.max, offerCount: p.variants.length,
      availability: p.stock > 0 ? "https://schema.org/InStock" : "https://schema.org/OutOfStock",
      ...(SITE_URL ? { url: abs(`/san-pham/${encodeURIComponent(p.id)}/`) } : {}),
    },
  };
  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(ld).replace(/</g, "\\u003c") }} />
      <ProductDetail key={p.id} p={p} updated={updated} related={related} />
    </>
  );
}
