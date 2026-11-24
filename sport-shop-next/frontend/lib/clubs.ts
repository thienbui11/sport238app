/* M7: tìm áo theo tên CLB / đội tuyển quen gọi ("mu", "man u", "barcelona", "đtvn"…).
   - data: chữ có trong tên sản phẩm Sapo (khớp NGUYÊN TỪ, giữ dấu – để "mũ" không bị hiểu là "MU").
   - alias: cách khách hay gõ. So không dấu; alias bắt đầu bằng "=" phải gõ đúng cả dấu (từ ngắn dễ trùng tiếng Việt: mu/mũ, anh/ánh).
   Thêm đội mới: thêm một dòng ở đây (tên sản phẩm trong Sapo phải có chữ ở "data"). */
import { fold } from "./shop";

export type Club = { name: string; q: string; data: string[]; alias: string[] };

export const CLUBS: Club[] = [
  { name: "Manchester United (MU)", q: "mu", data: ["mu"], alias: ["=mu", "man u", "manu", "man utd", "manchester united", "manchester", "quỷ đỏ"] },
  { name: "Manchester City (MC)", q: "man city", data: ["mc"], alias: ["=mc", "man city", "manchester city", "manchester", "city"] },
  { name: "Real Madrid", q: "real madrid", data: ["real"], alias: ["real", "real madrid", "madrid", "los blancos", "kền kền trắng"] },
  { name: "Barcelona (Barca)", q: "barcelona", data: ["barca", "barça", "barcelona"], alias: ["barca", "barça", "barcelona", "fc barcelona"] },
  { name: "Bayern Munich", q: "bayern", data: ["bayern"], alias: ["bayern", "bayern munich", "munich", "munchen"] },
  { name: "Liverpool", q: "liverpool", data: ["liverpool"], alias: ["liverpool", "lfc", "lữ đoàn đỏ"] },
  { name: "Chelsea", q: "chelsea", data: ["chelsea"], alias: ["chelsea", "cfc", "the blues"] },
  { name: "Arsenal", q: "arsenal", data: ["arsenal"], alias: ["arsenal", "pháo thủ"] },
  { name: "Paris Saint-Germain (PSG)", q: "psg", data: ["psg"], alias: ["psg", "paris", "paris saint germain", "paris sg"] },
  { name: "Inter Milan", q: "inter milan", data: ["inter"], alias: ["inter", "inter milan", "milan"] },
  { name: "AC Milan", q: "ac milan", data: ["ac milan"], alias: ["ac milan", "milan"] },
  { name: "Tottenham", q: "tottenham", data: ["tottenham"], alias: ["tottenham", "spurs", "gà trống"] },
  { name: "Wolves", q: "wolves", data: ["wolves"], alias: ["wolves", "wolverhampton", "bầy sói"] },
  { name: "Chicago Bulls (bóng rổ)", q: "chicago bulls", data: ["bulls"], alias: ["bulls", "chicago", "chicago bulls"] },
  { name: "Tây Ban Nha", q: "tây ban nha", data: ["tây ban nha"], alias: ["tây ban nha", "tbn", "spain", "españa"] },
  { name: "Argentina", q: "argentina", data: ["argentina"], alias: ["argentina", "arg", "albiceleste"] },
  { name: "Hà Lan", q: "hà lan", data: ["hà lan"], alias: ["hà lan", "netherlands", "holland", "oranje"] },
  { name: "Brazil", q: "brazil", data: ["brazil"], alias: ["brazil", "brasil"] },
  { name: "Bồ Đào Nha", q: "bồ đào nha", data: ["bồ đào nha"], alias: ["bồ đào nha", "bdn", "portugal"] },
  { name: "Pháp", q: "pháp", data: ["pháp"], alias: ["pháp", "france"] },
  { name: "Đức", q: "đức", data: ["đức"], alias: ["=đức", "germany", "cỗ xe tăng"] },
  { name: "Nhật Bản", q: "nhật", data: ["nhật"], alias: ["nhật", "nhật bản", "japan"] },
  { name: "Hàn Quốc", q: "hàn quốc", data: ["hàn quốc"], alias: ["hàn quốc", "korea"] },
  { name: "Mỹ", q: "mỹ", data: ["mỹ"], alias: ["=mỹ", "usa", "hoa kỳ", "america"] },
  { name: "Bỉ", q: "bỉ", data: ["bỉ"], alias: ["=bỉ", "belgium"] },
  { name: "Việt Nam", q: "việt nam", data: ["vn", "việt nam"], alias: ["việt nam", "=vn", "đtvn", "đội tuyển việt nam"] },
  { name: "Anh (England)", q: "england", data: ["anh"], alias: ["=anh", "england", "tam sư"] },
];

const norm = (s: string) => (s ?? "").normalize("NFC").toLowerCase().replace(/\s+/g, " ").trim();
const esc = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
/** Có cụm w đứng riêng (không dính chữ/số khác) trong t */
const hasWord = (t: string, w: string) => new RegExp(`(?<![\\p{L}\\p{N}])${esc(w)}(?![\\p{L}\\p{N}])`, "u").test(t);

/** Các đội của một sản phẩm (theo tên) */
export const clubsOf = (title: string, name: string) => {
  const t = norm(`${title} ${name}`);
  return CLUBS.filter((c) => c.data.some((d) => hasWord(t, d)));
};

/** Tách tên đội trong câu tìm: trả về các đội nhắc tới và phần chữ còn lại (để tìm bình thường).
 *  Cụm dài xét trước ("inter milan" trước "milan"). */
export function parseClubQuery(q: string): { clubs: Club[]; rest: string } {
  let raw = norm(q), folded = fold(raw);
  const found = new Set<Club>();
  const all = CLUBS.flatMap((c) => c.alias.map((a) => ({ c, exact: a.startsWith("="), a: norm(a.replace(/^=/, "")) })))
    .sort((x, y) => y.a.length - x.a.length);
  for (const { c, exact, a } of all) {
    const target = exact ? raw : folded, key = exact ? a : fold(a);
    const re = new RegExp(`(?<![\\p{L}\\p{N}])${esc(key)}(?![\\p{L}\\p{N}])`, "u");
    const m = target.match(re);
    if (!m || m.index === undefined) continue;
    // cùng cụm có thể thuộc nhiều đội (vd "milan", "manchester"): ghi nhận mọi đội có cụm này rồi mới xóa khỏi câu
    for (const o of all) if ((o.exact ? o.a === key && exact : fold(o.a) === key && !o.exact)) found.add(o.c);
    found.add(c);
    const cut = (s: string) => (s.slice(0, m.index) + " " + s.slice(m.index! + m[0].length)).replace(/\s+/g, " ").trim();
    raw = cut(raw); folded = cut(folded);
  }
  return { clubs: [...found], rest: folded };
}

/** Gợi ý khi đang gõ: đội có tên/cách gọi bắt đầu bằng chữ đang gõ (≥ 2 ký tự) */
export function suggestClubs(q: string): Club[] {
  const f = fold(norm(q));
  if (f.length < 2) return [];
  return CLUBS.filter((c) => [c.name, ...c.alias.map((a) => a.replace(/^=/, ""))].some((a) => fold(norm(a)).split(/[\s()]+/).some((w, i, ws) => ws.slice(i).join(" ").startsWith(f))));
}
