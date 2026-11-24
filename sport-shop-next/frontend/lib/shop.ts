import raw from "../data/products.json";
import rawImages from "../data/images.json";

/** 9 danh mục của web. Thứ tự và biểu tượng (SVG trong components/Icons.tsx) sửa ở đây. Tên phải khớp với tên danh mục trong dữ liệu. */
export type CatIconName = "trophy" | "boot" | "sneaker" | "jersey" | "tee" | "kids" | "bag" | "sock" | "shuttle";
export const CATEGORIES: readonly { name: string; icon: CatIconName }[] = [
  { name: "Cờ, Cúp, Huy Chương", icon: "trophy" },
  { name: "Giày bóng đá", icon: "boot" },
  { name: "Giày thể thao", icon: "sneaker" },
  { name: "Quần áo CLB/Đội tuyển", icon: "jersey" },
  { name: "Quần áo không logo", icon: "tee" },
  { name: "Quần áo trẻ em", icon: "kids" },
  { name: "Phụ kiện thể thao", icon: "bag" },
  { name: "Vớ/tất ống đồng", icon: "sock" },
  { name: "Cầu lông", icon: "shuttle" },
];
export const ICON_OF: Record<string, CatIconName> = Object.fromEntries(CATEGORIES.map((c) => [c.name, c.icon]));
/** Danh mục mà khách cần chọn size */
export const NEED_SIZE = ["Giày bóng đá", "Giày thể thao", "Quần áo CLB/Đội tuyển", "Quần áo không logo", "Quần áo trẻ em"];

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
/** Giờ mở cửa (khách phải ghé shop nhận hàng nên ghi ở nhiều chỗ) */
export const HOURS = { time: "8:00–21:00", days: "tất cả các ngày trong tuần" };
/** Số sản phẩm hiện mỗi lần; bấm "Xem thêm" để hiện tiếp */
export const PAGE = 20;
/** Không chặn khi vượt tồn kho (tồn trên web có thể chưa kịp cập nhật): vẫn cho thêm, cảnh báo rõ */
export const OVER = "Số lượng vượt tồn kho trên web, shop sẽ kiểm tra lại khi chốt đơn";
/** Bỏ dấu tiếng Việt để tìm kiếm: "Giày" -> "giay", "Đỏ" -> "do" */
export const fold = (s: string) => (s ?? "").toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/đ/g, "d");
export const links = (s: Site) => ({
  zalo: `https://zalo.me/${s.zalo}`,
  messenger: `https://m.me/${s.messenger}`,
  page: `https://www.facebook.com/${s.messenger}`,
  map: `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(s.address)}`,
});

export type Variant = { id: string; sku: string; size: string; color: string; price: number; stock: number };
export type Product = {
  id: string; name: string; title: string; cat: string; brand: string; desc: string; feat: boolean;
  variants: Variant[]; colors: string[]; sizes: string[]; min: number; max: number; stock: number;
  images: Record<string, string[]>;
  /** chuỗi không dấu để tìm: tên, hãng, danh mục, mã, màu */
  key: string;
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
    updated: process.env.CAP_NHAT_NGAY || d.updated || "",
  };
}

type Base = Pick<Product, "id" | "name" | "title" | "cat" | "brand" | "desc" | "feat" | "variants" | "images">;
/** Tính các trường suy ra (màu, size, giá thấp/cao, tồn, chuỗi tìm kiếm) – dùng chung cho máy chủ và trình duyệt */
function build(b: Base): Product {
  const prices = b.variants.map((v) => v.price), colors = uniq(b.variants.map((v) => v.color));
  return {
    ...b, key: fold([b.name, b.title, b.brand, b.cat, b.id, ...b.variants.map((v) => v.sku), ...colors].join(" ")),
    colors, sizes: uniq(b.variants.map((v) => v.size)).sort((a, c) => sizeKey(a) - sizeKey(c)),
    min: Math.min(...prices), max: Math.max(...prices), stock: b.variants.reduce((a, v) => a + v.stock, 0),
  };
}
const imagesOf = (imgs: Record<string, string[]>, id: string) => Object.fromEntries(Object.entries(imgs).filter(([k]) => k === id || k.startsWith(id + ":")));

export async function getCatalog(): Promise<{ products: Product[]; updated: string }> {
  const d = await getPublicCatalog();
  const products = d.products.map((x) => build({
    id: x.id, name: x.display_title || x.title, title: x.title, cat: x.category && ICON_OF[x.category] ? x.category : "Phụ kiện thể thao",
    brand: x.vendor, desc: x.description ?? "", feat: !!x.featured,
    variants: x.variants.map((v) => ({ id: v.id, sku: v.sku || v.id, size: v.option1, color: v.option2, price: v.price, stock: Math.max(0, v.inventory_quantity) })),
    images: imagesOf(d.images, x.id),
  }));
  return { products, updated: d.updated ?? "" };   // d.updated đã tính cả CAP_NHAT_NGAY
}

/** Dạng gọn để gửi danh sách sản phẩm xuống trình duyệt (trang chủ): nhỏ hơn khoảng 4 lần, trang tải và chạy nhanh hơn.
 *  Mỗi SP: [mã, tên, tên Sapo ("" nếu giống tên), số thứ tự danh mục, hãng, nổi bật 0/1, các màu, các size,
 *  các phiên bản [mã, số thứ tự màu, số thứ tự size, giá, tồn, (SKU nếu khác mã)]]. Không có mô tả (thẻ không dùng). */
type PackedVariant = [string, number, number, number, number, string?];
export type Packed = { p: [string, string, string, number, string, number, string[], string[], PackedVariant[]][]; i: Record<string, string[]> };
export const pack = (ps: Product[]): Packed => ({
  p: ps.map((p) => [p.id, p.name, p.title === p.name ? "" : p.title, CATEGORIES.findIndex((c) => c.name === p.cat), p.brand, p.feat ? 1 : 0, p.colors, p.sizes,
    p.variants.map((v): PackedVariant => { const t: PackedVariant = [v.id, p.colors.indexOf(v.color), p.sizes.indexOf(v.size), v.price, v.stock]; if (v.sku !== v.id) t.push(v.sku); return t; })]),
  i: Object.assign({}, ...ps.map((p) => p.images)),
});
export const unpack = (d: Packed): Product[] => d.p.map(([id, name, title, ci, brand, feat, colors, sizes, vs]) => build({
  id, name, title: title || name, cat: CATEGORIES[ci]?.name ?? "Phụ kiện thể thao", brand, desc: "", feat: !!feat,
  variants: vs.map(([vid, c, s, price, stock, sku]) => ({ id: vid, sku: sku ?? vid, size: sizes[s], color: colors[c], price, stock })),
  images: imagesOf(d.i, id),
}));

/** Địa chỉ web thật (vd https://sport238.vn), dùng cho Open Graph, canonical, sitemap. Để trống thì bỏ các phần cần URL tuyệt đối. */
export const SITE_URL = (process.env.SITE_URL ?? "").trim().replace(/\/+$/, "");
export const abs = (path: string) => (SITE_URL ? SITE_URL + path : "");

export const money = (n: number) => n.toLocaleString("vi-VN") + "đ";
export const phone = (z: string) => z.replace(/^(\d{4})(\d{3})(\d{3,4})$/, "$1 $2 $3");
export const hueOf = (s: string) => [...s].reduce((h, c) => (h * 31 + c.charCodeAt(0)) % 360, 0);
export const imgsFor = (p: Product, color: string) => p.images[`${p.id}:${color}`] ?? p.images[p.id] ?? [];
export const priceText = (p: Product) => (p.min !== p.max ? "Từ " : "") + money(p.min);
export const stockStatus = (p: Product): [string, string] => (p.stock <= 0 ? ["Hết hàng", "out"] : p.stock <= 5 ? ["Sắp hết", "warn"] : ["Còn hàng", ""]);
export function sizeGroup(cat: string, s: string): string {
  if (cat === "Giày bóng đá" || cat === "Giày thể thao" || !s) return "";
  if (/^\d+$/.test(s)) return "Trẻ em";
  return /^(XS|S|M|L|XL|XXL|XXXL|XXXXL|[2-6]XL)$/i.test(s) ? "Người lớn" : "";
}

export const colorStock = (p: Product, c: string) => p.variants.filter((v) => v.color === c).reduce((a, v) => a + v.stock, 0);
export const defaultColor = (p: Product) => p.colors.find((c) => colorStock(p, c) > 0) ?? p.colors[0];
/** Biến thể có phải là màu không; nếu là mẫu/loại thì gọi là "Loại" thay vì "Màu" */
const COLOR_WORDS = /(trắng|đen|đỏ|xanh|vàng|cam|tím|hồng|xám|nâu|be|kem|navy|sen|bã trầu|cổ vịt|rêu|bích|ghi|bạc|chuối|lam|lục|ngọc|white|black|red|blue)/i;
export const optLabel = (p: Product) => (p.colors.every((c) => COLOR_WORDS.test(c)) ? "Màu" : "Loại");

/* ===== Màu sản phẩm → mã màu, để tô hình minh họa và chấm màu khi CHƯA có ảnh thật ===== */
const HEX: Record<string, string> = {
  "xanh đen": "#1f2a44", "xanh navy": "#1f2a5c", navy: "#1f2a5c", "xanh dương": "#1e5fc2", "xanh biển": "#1b6cc0", "xanh lam": "#2a63c9",
  "xanh bích": "#2370d8", bích: "#2370d8", "xanh cổ vịt": "#0e7c86", "cổ vịt": "#0e7c86", "xanh ngọc": "#12a594", ngọc: "#12a594",
  "xanh rêu": "#55652e", rêu: "#55652e", "xanh lá": "#2e9d4b", "thiên thanh": "#6cb4e4", "lông công": "#0f6b78", xanh: "#1e5fc2",
  "đỏ đô": "#7f0d1f", đô: "#7f0d1f", đỏ: "#d0202e", trắng: "#f5f5f3", đen: "#1d1d1f", kem: "#efe5cc", be: "#d9c4a0", "bã trầu": "#7a3b22",
  xám: "#8d8d92", ghi: "#8d8d92", bạc: "#c0c0c4", vàng: "#f2c230", cam: "#f07a1c", "tím nhạt": "#b39ddb", tím: "#6d3fa6",
  hồng: "#ec7aa7", sen: "#e4609a", nâu: "#7b5235", white: "#f5f5f3", black: "#1d1d1f", red: "#d0202e", blue: "#1e5fc2",
};
const HEX_RE = new RegExp(String.raw`(?<![\p{L}\p{N}])(` + Object.keys(HEX).sort((a, b) => b.length - a.length).join("|") + String.raw`)(?![\p{L}\p{N}])`, "gu");
/** Các mã màu nhận ra trong một chuỗi ("Trắng-Navy Sen" → trắng, navy, sen), theo thứ tự xuất hiện, không trùng */
export function hexesIn(s: string): string[] {
  const out: string[] = [];
  for (const m of (s ?? "").normalize("NFC").toLowerCase().matchAll(HEX_RE)) { const h = HEX[m[1]]; if (!out.includes(h)) out.push(h); }
  return out;
}
/** Màu để tô hình minh họa: theo tên màu/loại đang chọn, nếu không có thì theo tên sản phẩm */
export const artColors = (p: Product, color: string): string[] => {
  const a = hexesIn(color);
  return a.length ? a : hexesIn(p.name);
};
