"use client";
/* Bộ hình minh họa sản phẩm, vẽ MỘT lần mỗi trang (khung 200×200); thẻ sản phẩm dùng lại bằng <use href="#art-…">.
   Màu lấy từ biến CSS đặt trên thẻ <svg class="art"> (xem Art trong Icons.tsx):
   --a màu chính · --b màu phụ (cổ áo, đế, sọc) · --n màu số áo · --l màu dây giày/vân · màu nét = currentColor (--ph-stroke).
   Không dùng emoji; không id nào khác ngoài id của từng hình. */
import type { CSSProperties } from "react";

const A: CSSProperties = { fill: "var(--a)" }, B: CSSProperties = { fill: "var(--b)" };
const SH = "rgba(0,0,0,.09)", HI = "rgba(255,255,255,.4)";
const FLOOR = <ellipse cx="100" cy="176" rx="66" ry="7" stroke="none" style={{ fill: "var(--ph-shadow)" }} />;
const NUM: CSSProperties = { fill: "var(--n)", fontFamily: "var(--font), system-ui, sans-serif" };
const JERSEY = "M72 36 50 43 26 64l14 26 16-9v81q0 5 5 5h78q5 0 5-5V81l16 9 14-26-24-21-22-7q-7 14-28 15-21-1-28-15z";

function Jersey({ crest, num }: { crest?: boolean; num: string }) {
  return (
    <>
      <path style={A} d={JERSEY} />
      <path fill={SH} stroke="none" d="M124 50l4-14 22 7 24 21-14 26-16-9v81q0 5-5 5h-15z" />
      <path style={B} d="M26 64l14 26 7.8-4.4-15-27.5zM174 64l-14 26-7.8-4.4 15-27.5z" />
      <path fill="rgba(0,0,0,.2)" stroke="none" d="M76 37q24 11 48 0-4 11-24 12-20-1-24-12z" />
      <path fill="none" style={{ stroke: "var(--b)" }} strokeWidth={6} d="M73 37q7 14 27 14t27-14" />
      {crest && <path style={B} strokeWidth={2} d="M117 66h14v8q0 7-7 10-7-3-7-10z" />}
      <text x="100" y={crest ? 126 : 120} textAnchor="middle" fontSize={crest ? 27 : 32} fontWeight={800} stroke="none" letterSpacing="-1" style={NUM}>{num}</text>
      <path fill="none" d={JERSEY} />
    </>
  );
}

const LACES = <path fill="none" style={{ stroke: "var(--l)" }} strokeWidth={3.5} d="M120 77l9 9M114 84l9 9M108 91l9 9" />;

const ART: Record<string, React.ReactNode> = {
  jersey: <Jersey crest num="238" />,
  tee: <Jersey num="238" />,
  kids: <g transform="translate(22 40) scale(.78)"><Jersey num="8" /></g>,
  boot: (
    <>
      <path style={A} d="M30 132c-2-20 10-30 28-32l28-4c6-12 14-22 26-26l16 2c4 16 16 26 34 32l16 6c10 4 12 16 6 24l-4 4-146 2c-4-1-4-4-4-8z" />
      <path fill={SH} stroke="none" d="M31 124h153c1 5-1 9-4 12l-146 2c-3-1-3-6-3-14z" />
      <path fill="rgba(0,0,0,.35)" stroke="none" d="M87 95c9-10 16-18 25-23l15 2c-7 7-23 19-39 26z" />
      <path fill="none" style={{ stroke: "var(--b)" }} strokeWidth={7} d="M50 124c36 2 70-4 108-17" />
      {LACES}
      <path style={B} d="M32 139l150-2c2 4 0 9-6 9l-138 1c-5 0-7-3-6-8z" />
      <path style={B} strokeWidth={2.5} d="M44 147h10v8H44zM66 147h10v8H66zM114 146h10v8h-10zM138 146h10v8h-10zM160 146h10v8h-10z" />
    </>
  ),
  sneaker: (
    <>
      <path style={A} d="M30 128c-2-18 10-28 28-30l28-4c6-12 14-20 26-24l16 2c4 16 16 24 34 30l14 6c10 4 12 14 8 20z" />
      <path fill="rgba(0,0,0,.3)" stroke="none" d="M87 93c9-10 16-17 25-21l15 2c-7 7-23 17-39 24z" />
      <path fill="none" style={{ stroke: "var(--b)" }} strokeWidth={7} d="M52 118c34 0 66-6 102-17" />
      {LACES}
      <path fill="#f4f2ef" d="M28 126h158c2 8-2 16-10 16H36c-6 0-9-6-8-16z" />
      <path style={B} d="M34 142h144c-2 6-6 8-12 8H42c-4 0-7-3-8-8z" />
    </>
  ),
  sock: (
    <>
      <path style={A} d="M74 24h48v88c0 8 4 14 12 18l30 14c14 7 16 22 6 30-8 7-20 6-30 1l-54-27c-8-4-12-12-12-22z" />
      <path fill={SH} stroke="none" d="M108 24h14v88c0 8 4 14 12 18l30 14c6 3 10 8 11 13-28-8-54-22-67-40z" />
      <path style={B} d="M74 24h48v18H74zM74 50h48v7H74z" />
      <path fill="none" style={{ stroke: "var(--l)" }} strokeWidth={3} strokeDasharray="1 9" d="M80 132l50 24M86 122l50 24" />
    </>
  ),
  trophy: (
    <>
      <path fill="none" style={{ stroke: "var(--a)" }} strokeWidth={8} d="M64 46c-22 0-24 34 4 36M136 46c22 0 24 34-4 36" />
      <path style={A} d="M62 34h76v22c0 32-16 48-38 52-22-4-38-20-38-52z" />
      <path fill={SH} stroke="none" d="M104 34h34v22c0 32-16 48-38 52 14-8 18-30 4-74z" />
      <path fill="none" stroke={HI} strokeWidth={5} d="M76 42c0 26 4 42 14 52" />
      <path style={A} d="M92 106h16l3 26H89zM72 132h56v14H72z" />
      <path style={B} d="M64 146h72v16H64z" />
    </>
  ),
  bag: (
    <>
      <path fill="none" style={{ stroke: "var(--b)" }} strokeWidth={8} d="M76 78c0-30 48-30 48 0" />
      <path style={A} d="M36 94c0-12 10-18 22-18h84c12 0 22 6 22 18v52c0 8-6 14-14 14H50c-8 0-14-6-14-14z" />
      <path fill={SH} stroke="none" d="M120 76h22c12 0 22 6 22 18v52c0 8-6 14-14 14h-30z" />
      <path style={B} stroke="none" d="M37 114h126v12H37z" />
      <path fill="none" stroke={HI} strokeWidth={3} d="M52 92h96" />
    </>
  ),
  shuttle: (
    <>
      <path style={A} d="M84 132 58 42h84l-26 90z" />
      <path fill="none" strokeOpacity={0.45} strokeWidth={2.5} d="M92 132 76 42M100 132V42M108 132l16-90M64 64h72M72 92h56" />
      <path style={B} d="M82 130h36v10H82z" />
      <path fill="#f1e9dc" d="M82 140h36c0 24-36 24-36 0z" />
    </>
  ),
};

/** dời hình xuống cho chạm bóng đổ dưới chân */
const DY: Record<string, number> = { boot: 14, sneaker: 18, trophy: 8, bag: 10, shuttle: 12, kids: 0 };

export default function ArtSprite() {
  return (
    <svg width="0" height="0" style={{ position: "absolute", overflow: "hidden" }} aria-hidden="true" focusable="false">
      <defs>
        {Object.entries(ART).map(([k, body]) => (
          <symbol key={k} id={`art-${k}`} viewBox="0 0 200 200">
            {FLOOR}
            <g stroke="currentColor" strokeWidth={3} strokeLinejoin="round" strokeLinecap="round" transform={`translate(0 ${DY[k] ?? 0})`}>{body}</g>
          </symbol>
        ))}
      </defs>
    </svg>
  );
}
