import { getPublicCatalog } from "@/lib/shop";

// Giống tệp products.json của web tĩnh (bản HTML thuần): giỏ hàng dùng để lấy giá, tồn kho mới nhất.
export const revalidate = 60;
export const dynamic = "force-static";

export async function GET() {
  return Response.json(await getPublicCatalog());
}
