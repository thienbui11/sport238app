import raw from "../data/products.json";
import rawImages from "../data/images.json";

/** 8 danh mục của web. Thứ tự và màu ô danh mục sửa ở đây. Tên phải khớp với tên danh mục trong dữ liệu. */
export const CATEGORIES = [
  { name: "Cờ, Cúp, Huy Chương", emoji: "🏆", c1: "#7c5a10", c2: "#c99a2e" },
  { name: "Giày bóng đá", emoji: "👟", c1: "#a3122a", c2: "#d63a50" },
  { name: "Quần áo CLB/Đội tuyển", emoji: "⚽", c1: "#2b2b30", c2: "#55555e" },
  { name: "Quần áo không logo", emoji: "👕", c1: "#8a0f23", c2: "#bd2a3f" },
  { name: "Quần áo trẻ em", emoji: "🧒", c1: "#c2410c", c2: "#f0883e" },
  { name: "Phụ kiện thể thao", emoji: "🎒", c1: "#3a3a40", c2: "#1d1d20" },
  { name: "Vớ/tất ống đồng", emoji: "🧦", c1: "#b3202f", c2: "#e0566a" },
  { name: "Cầu lông", emoji: "🏸", c1: "#0f6a45", c2: "#2faa6f" },
] as const;
export const EMO: Record<string, string> = Object.fromEntries(CATEGORIES.map((c) => [c.name, c.emoji]));
/** Danh mục mà khách cần chọn size */
export const NEED_SIZE = ["Giày bóng đá", "Quần áo CLB/Đội tuyển", "Quần áo không logo", "Quần áo trẻ em"];

/** Nhận cả tên ("Sport238") lẫn đường dẫn đầy đủ ("https://www.facebook.com/Sport238"), luôn trả về tên trang */
export function fbUser(v: string): string {
  v = (v ?? "").trim();
  const m = v.match(/(?:facebook\.com|fb\.com|m\.me)\/(?:profile\.php\?id=)?([^/?#&\s]+)/i);
  return (m ? m[1] : v).replace(/^@/, "");
}

export const DEFAULT_SITE = {
  name: "SPORT 238",
  zalo: "0962374770",
  messenger: fbUser(process.env.NEXT_PUBLIC_MESSENGER_USER ?? "Sport238"),
  address: "238 ấp Thuận Điền, xã Phú Túc, tỉnh Vĩnh Long (Ngã 3 KCN An Hiệp)",
};
export type Site = typeof DEFAULT_SITE;
export const links = (s: Site) => ({
  zalo: `https://zalo.me/${s.zalo}`,
  messenger: `https://m.me/${s.messenger}`,
  page: `https://www.facebook.com/${s.messenger}`,
  map: `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(s.address)}`,
});

export type Variant = { id: string; sku: string; size: string; color: string; price: number; stock: number };
export type Product = {
  id: string; name: string; cat: string; brand: string; desc: string; feat: boolean;
  variants: Variant[]; colors: string[]; sizes: string[]; min: number; max: number; stock: number;
  images: Record<string, string[]>;
};

type ApiVariant = { id: string; sku?: string; option1: string; option2: string; price: number; inventory_quantity: number };
type ApiProduct = { id: string; title: string; display_title?: string; description?: string; category?: string; vendor: string; featured?: boolean; variants: ApiVariant[] };
type ApiCatalog = { products: ApiProduct[]; images?: Record<string, string[]>; updated?: string };

const API = process.env.API_URL;

async function load<T>(path: string, fallback: T): Promise<T> {
  if (!API) return fallback;
  try {
    const r = await fetch(API + path, { next: { revalidate: 60 } });
    return r.ok ? ((await r.json()) as T) : fallback;
  } catch {
    return fallback;
  }
}

export async function getSite(): Promise<Site> {
  const c = await load<{ shopName?: string; zaloPhone?: string; messengerUser?: string } | null>("/api/config", null);
  if (!c) return DEFAULT_SITE;
  return {
    ...DEFAULT_SITE,
    name: c.shopName || DEFAULT_SITE.name,
    zalo: (c.zaloPhone || DEFAULT_SITE.zalo).replace(/\s+/g, ""),
    messenger: fbUser(c.messengerUser || "") || DEFAULT_SITE.messenger,
  };
}

const uniq = <T,>(a: T[]) => a.filter((x, i) => a.indexOf(x) === i);
const ADULT = ["S", "M", "L", "XL", "XXL", "XXXL", "XXXXL"];
export const sizeKey = (s: string) => (isNaN(+s) ? 100 + ADULT.indexOf(s) : +s);

/** Dữ liệu công khai đúng như GET /api/products. Chỉ giữ các trường được phép (không bao giờ có giá nhập, giá vốn, giá buôn). */
export async function getPublicCatalog(): Promise<ApiCatalog & { images: Record<string, string[]>; updated: string }> {
  const d = await load<ApiCatalog>("/api/products", raw as unknown as ApiCatalog);
  return {
    products: d.products.map((x) => ({
      id: x.id, title: x.title, display_title: x.display_title, description: x.description, category: x.category, vendor: x.vendor, featured: x.featured,
      variants: x.variants.map((v) => ({ id: v.id, sku: v.sku, option1: v.option1, option2: v.option2, price: v.price, inventory_quantity: v.inventory_quantity })),
    })),
    images: { ...(rawImages as Record<string, string[]>), ...(d.images ?? {}) },
    updated: d.updated ?? "",
  };
}

export async function getCatalog(): Promise<{ products: Product[]; updated: string }> {
  const d = await getPublicCatalog();
  const imgs = d.images;
  const products = d.products.map((x): Product => {
    const variants = x.variants.map((v) => ({ id: v.id, sku: v.sku || v.id, size: v.option1, color: v.option2, price: v.price, stock: Math.max(0, v.inventory_quantity) }));
    const prices = variants.map((v) => v.price);
    return {
      id: x.id, name: x.display_title || x.title, cat: x.category && EMO[x.category] ? x.category : "Phụ kiện thể thao",
      brand: x.vendor, desc: x.description ?? "", feat: !!x.featured,
      variants, colors: uniq(variants.map((v) => v.color)), sizes: uniq(variants.map((v) => v.size)).sort((a, b) => sizeKey(a) - sizeKey(b)),
      min: Math.min(...prices), max: Math.max(...prices), stock: variants.reduce((a, v) => a + v.stock, 0),
      images: Object.fromEntries(Object.entries(imgs).filter(([k]) => k === x.id || k.startsWith(x.id + ":"))),
    };
  });
  return { products, updated: d.updated ?? "" };
}

export const money = (n: number) => n.toLocaleString("vi-VN") + "đ";
export const phone = (z: string) => z.replace(/^(\d{4})(\d{3})(\d{3,4})$/, "$1 $2 $3");
export const hueOf = (s: string) => [...s].reduce((h, c) => (h * 31 + c.charCodeAt(0)) % 360, 0);
export const imgsFor = (p: Product, color: string) => p.images[`${p.id}:${color}`] ?? p.images[p.id] ?? [];
export const priceText = (p: Product) => (p.min !== p.max ? "Từ " : "") + money(p.min);
export const stockStatus = (p: Product): [string, string] => (p.stock <= 0 ? ["Hết hàng", "out"] : p.stock <= 5 ? ["Sắp hết", "warn"] : ["Còn hàng", ""]);
export function sizeGroup(cat: string, s: string): string {
  if (cat === "Giày bóng đá" || !s) return "";
  if (/^\d+$/.test(s)) return "Trẻ em";
  return /^(XS|S|M|L|XL|XXL|XXXL|XXXXL|[2-6]XL)$/i.test(s) ? "Người lớn" : "";
}

export const colorStock = (p: Product, c: string) => p.variants.filter((v) => v.color === c).reduce((a, v) => a + v.stock, 0);
export const defaultColor = (p: Product) => p.colors.find((c) => colorStock(p, c) > 0) ?? p.colors[0];
/** Biến thể có phải là màu không; nếu là mẫu/loại thì gọi là "Loại" thay vì "Màu" */
const COLOR_WORDS = /(trắng|đen|đỏ|xanh|vàng|cam|tím|hồng|xám|nâu|be|kem|navy|sen|bã trầu|cổ vịt|rêu|bích|ghi|bạc|chuối|lam|lục|ngọc|white|black|red|blue)/i;
export const optLabel = (p: Product) => (p.colors.every((c) => COLOR_WORDS.test(c)) ? "Màu" : "Loại");
