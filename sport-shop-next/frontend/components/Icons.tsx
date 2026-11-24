"use client";
/* Biểu tượng SVG nội tuyến (không dùng emoji làm hình trang trí: emoji vẽ khác nhau trên mỗi máy và làm chậm trang).
   - <Icon n="…" />: biểu tượng giao diện 24×24, nét theo màu chữ (currentColor), cỡ theo cỡ chữ (1em).
   - <CatIcon n="…" />: biểu tượng 9 danh mục.
   - <Art kind="…" c1 c2 />: hình minh họa sản phẩm khi CHƯA có ảnh thật (tô theo màu của sản phẩm nếu biết).
   Không dùng id trong SVG (nhiều thẻ cùng lúc trên trang sẽ trùng id). */
import type { CatIconName } from "@/lib/shop";

const UI = {
  search: "M10.5 4a6.5 6.5 0 1 0 0 13 6.5 6.5 0 1 0 0-13zM15.5 15.5 20 20",
  cart: "M3 4h2.2l2.1 10.2a1.6 1.6 0 0 0 1.6 1.3h8.3a1.6 1.6 0 0 0 1.6-1.2L20.5 8H6.1M9 19.5h.01M17 19.5h.01",
  menu: "M4 7h16M4 12h16M4 17h16",
  close: "M6 6l12 12M18 6 6 18",
  chat: "M6.5 3.5h11a2.5 2.5 0 0 1 2.5 2.5v7.5a2.5 2.5 0 0 1-2.5 2.5H11l-4.5 4v-4A2.5 2.5 0 0 1 4 13.5V6a2.5 2.5 0 0 1 2.5-2.5zM8.5 9.5h7M8.5 12.5h4",
  messenger: "M12 3.2c-5 0-8.8 3.6-8.8 8.2 0 2.5 1.1 4.6 3 6.1v3.3l3-1.6c.9.3 1.8.4 2.8.4 5 0 8.8-3.6 8.8-8.2S17 3.2 12 3.2zM7.6 13.6l3.1-3.3 2.3 2.2 3.4-2.2-3.1 3.3-2.3-2.2z",
  facebook: "M14.5 8.5h2.5V5h-2.5A3.5 3.5 0 0 0 11 8.5V11H8.5v3.5H11V21h3.5v-6.5H17l.5-3.5h-3V9a.5.5 0 0 1 .5-.5z",
  pin: "M12 21s-6.5-5.8-6.5-11a6.5 6.5 0 0 1 13 0c0 5.2-6.5 11-6.5 11zM12 7.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 1 0 0-5z",
  clock: "M12 3a9 9 0 1 0 0 18 9 9 0 1 0 0-18zM12 7.5V12l3 2",
  left: "M14.5 5.5 8 12l6.5 6.5",
  right: "M9.5 5.5 16 12l-6.5 6.5",
  arrow: "M5 12h13.5M13 6.5l5.5 5.5-5.5 5.5",
  plus: "M12 5.5v13M5.5 12h13",
  minus: "M5.5 12h13",
  trash: "M4.5 7h15M9.5 7V4.8h5V7M6.5 7l.9 12.2a1.5 1.5 0 0 0 1.5 1.3h6.2a1.5 1.5 0 0 0 1.5-1.3L17.5 7M10.2 10.5v6.5M13.8 10.5v6.5",
  copy: "M9.5 8.5h9a1.5 1.5 0 0 1 1.5 1.5v9a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 8 19v-9a1.5 1.5 0 0 1 1.5-1.5zM16 8.5V5.5A1.5 1.5 0 0 0 14.5 4h-9A1.5 1.5 0 0 0 4 5.5v9A1.5 1.5 0 0 0 5.5 16H8",
  check: "M5 12.5 9.5 17 19 7.5",
  store: "M4.5 10.5V20h15v-9.5M3.5 4.5h17l1 4.2a2.8 2.8 0 0 1-5.3 1.4 2.8 2.8 0 0 1-4.2.9 2.8 2.8 0 0 1-4.2-.9 2.8 2.8 0 0 1-5.3-1.4zM10 20v-5h4v5",
  ruler: "M3.5 16.5 16.5 3.5l4 4-13 13zM7.5 12.5l2 2M10.5 9.5l2 2M13.5 6.5l2 2",
  box: "M3.5 7.5 12 3.5l8.5 4v9L12 20.5l-8.5-4zM3.5 7.5 12 11.5l8.5-4M12 11.5v9M7.8 5.5l8.4 4",
  map: "M3.5 11 20.5 3.5 13 20.5l-2-7.5z",
  warn: "M12 4 2.8 19.5h18.4zM12 10v4.5M12 17.2h.01",
  tag: "M3.5 12.2V4.5a1 1 0 0 1 1-1h7.7l8.3 8.3-8.7 8.7zM8 7.5h.01",
} as const;
export type IconName = keyof typeof UI;

export function Icon({ n, className }: { n: IconName; className?: string }) {
  return (
    <svg className={"i" + (className ? " " + className : "")} viewBox="0 0 24 24" width="1em" height="1em" fill="none" stroke="currentColor"
      strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false"><path d={UI[n]} /></svg>
  );
}

const CAT: Record<CatIconName, string> = {
  trophy: "M7 3.5h10v4.2a5 5 0 0 1-10 0zM7 5.5H4.5a3 3 0 0 0 3 4M17 5.5h2.5a3 3 0 0 1-3 4M12 12.7v3.3M8.5 20.5h7M9.5 16h5v4.5h-5z",
  boot: "M2.8 15.2c0-1.9 1.3-3 3.2-3h2.8l1.7-4.6c.3-.7 1-1 1.7-.8l1.8.5c.3 2 2 3.4 4.1 3.9l1.5.4c1.3.3 1.6 1.8 1 2.7l-.6.9H3.4a.6.6 0 0 1-.6-.6zM4.5 18.3v1.2M8.5 18.3v1.2M14 18.3v1.2M18 18.3v1.2M12.6 8.6l1.6 1M11.6 10.6l1.6 1",
  sneaker: "M2.8 14.2c0-1.9 1.3-3 3.2-3h2.8l1.7-4.6c.3-.7 1-1 1.7-.8l1.8.5c.3 2 2 3.4 4.1 3.9l1.5.4c1.3.3 1.9 1.9 1.4 3.6zM2.8 14.2v2.3c0 .8.7 1.5 1.5 1.5h15.6c.8 0 1.4-.6 1.4-1.4V14.2M12.6 7.6l1.6 1M11.6 9.6l1.6 1",
  jersey: "M8.2 3 4 5 1.8 9.4l3 1.5 1.2-1.6V21h12V9.3l1.2 1.6 3-1.5L20 5l-4.2-2c-.6 1.5-2 2.5-3.8 2.5S8.8 4.5 8.2 3zM14 9.5h2.2v1.6c0 .8-.5 1.3-1.1 1.6-.6-.3-1.1-.8-1.1-1.6z",
  tee: "M8.2 3 4 5 1.8 9.4l3 1.5 1.2-1.6V21h12V9.3l1.2 1.6 3-1.5L20 5l-4.2-2c-.6 1.5-2 2.5-3.8 2.5S8.8 4.5 8.2 3z",
  kids: "M9.4 6.5 6.6 7.8 5 10.8l2.1 1 .8-1.1v8.8h8.2v-8.8l.8 1.1 2.1-1-1.6-3-2.8-1.3c-.4 1-1.4 1.7-2.6 1.7S9.8 7.5 9.4 6.5zM12 2.5l.7 1.4 1.5.2-1.1 1 .3 1.5-1.4-.7-1.4.7.3-1.5-1.1-1 1.5-.2z",
  bag: "M3 9.8A2.8 2.8 0 0 1 5.8 7h12.4A2.8 2.8 0 0 1 21 9.8V17a2.5 2.5 0 0 1-2.5 2.5h-13A2.5 2.5 0 0 1 3 17zM8.5 7c0-2.4 1.5-3.6 3.5-3.6s3.5 1.2 3.5 3.6M3 13h18M10.5 13v2h3v-2",
  sock: "M8 2.5h7v9.2c0 .8.4 1.4 1 1.8l2.7 1.6c1.5.9 1.8 3 .6 4.2-.9.9-2.3 1.1-3.4.5l-6.5-3.6A3 3 0 0 1 8 13.6zM8 5.5h7M8 7.8h7",
  shuttle: "M9 15 6 3.5h12L15 15zM9 15h6v1.8a3 3 0 0 1-6 0zM10.3 3.5l.9 11.5M13.7 3.5l-.9 11.5M7 7.6h10M8 11.4h8",
};

export function CatIcon({ n }: { n: CatIconName }) {
  return (
    <svg className="i" viewBox="0 0 24 24" width="1em" height="1em" fill="none" stroke="currentColor" strokeWidth={1.7}
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false"><path d={CAT[n]} /></svg>
  );
}

/* ===== Hình minh họa sản phẩm: dùng lại các hình vẽ một lần trong ArtSprite.tsx (<symbol>), chỉ đổi màu bằng biến CSS ===== */
const lum = (hex: string) => {
  const n = parseInt(hex.slice(1), 16), ch = [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; });
  return 0.2126 * ch[0] + 0.7152 * ch[1] + 0.0722 * ch[2];
};
/** Màu viền phụ (cổ áo, đế giày) khi sản phẩm chỉ có một màu: nền sáng thì viền tối, nền tối thì viền sáng */
const pair = (c: string) => (lum(c) > 0.35 ? "#2b2b30" : "#f2f0ee");
const DEF: Record<CatIconName, [string, string]> = {
  trophy: ["#d9a72e", "#2b2b30"], boot: ["#2b2b30", "#a3122a"], sneaker: ["#f2f0ee", "#a3122a"],
  jersey: ["#dcd7d8", "#a3122a"], tee: ["#dcd7d8", "#a3122a"], kids: ["#dcd7d8", "#a3122a"],
  bag: ["#2b2b30", "#a3122a"], sock: ["#f2f0ee", "#a3122a"], shuttle: ["#f7f5f0", "#a3122a"],
};

/** Hình minh họa theo danh mục, tô theo màu sản phẩm (c1 màu chính, c2 màu phụ). Chỉ là hình thay thế khi chưa có ảnh thật. */
export function Art({ kind, c1, c2 }: { kind: CatIconName; c1?: string; c2?: string }) {
  const [d1, d2] = DEF[kind];
  const a = c1 ?? d1, b = c2 ?? (c1 ? pair(c1) : d2), light = lum(a) > 0.4;
  const style = { "--a": a, "--b": b, "--n": light ? "#232326" : "#ffffff", "--l": light ? "rgba(0,0,0,.25)" : "rgba(255,255,255,.45)" } as React.CSSProperties;
  return <svg className="art" viewBox="0 0 200 200" style={style} aria-hidden="true" focusable="false"><use href={`#art-${kind}`} /></svg>;
}
