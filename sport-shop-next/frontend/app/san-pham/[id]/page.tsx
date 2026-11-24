import { notFound } from "next/navigation";
import ProductDetail from "@/components/ProductDetail";
import { getCatalog } from "@/lib/shop";

export const revalidate = 60;

export async function generateStaticParams() {
  const { products } = await getCatalog();
  return products.map((p) => ({ id: p.id }));
}

type Props = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: Props) {
  const { id } = await params;
  const { products } = await getCatalog();
  const p = products.find((x) => x.id === decodeURIComponent(id));
  return { title: p ? `${p.name} | SPORT 238` : "SPORT 238" };
}

export default async function Page({ params }: Props) {
  const { id } = await params;
  const { products, updated } = await getCatalog();
  const p = products.find((x) => x.id === decodeURIComponent(id));
  if (!p) notFound();
  return <ProductDetail p={p} updated={updated} />;
}
