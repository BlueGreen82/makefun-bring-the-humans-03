// bring-the-humans-03 entry (Node 22, standard library only).
// It copies VIDEO.json from the repository root to /output/VIDEO.json,
// where the gate reads it. That is all the program has to do.
//
// The entry is the video itself: an original short vertical ad for make.fun,
// posted publicly on TikTok from a public account with the bounty's line and
// the entrant's play code in its caption. VIDEO.json names the video and the
// house reads its views from TikTok. Nothing this program writes is scored.
//
// The ad (ad.mp4, made by render_ad.py in this repository) shows make.fun's
// brand badge from its first frame and ends on make.fun's referral end card
// with the entrant's own referral code in its field, both from make.fun's
// press pack and used as they are.
//
// Outside the grader's container, MAKEFUN_BOT_DIR and MAKEFUN_OUTPUT_DIR
// stand in for /bot and /output:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = process.env.MAKEFUN_BOT_DIR ?? dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const src = join(root, "VIDEO.json");

// Fail loudly instead of copying a broken file: VIDEO.json must parse and
// carry a url string (a placeholder is fine here — it is replaced with the
// posted video's address before the entry is submitted).
const parsed = JSON.parse(readFileSync(src, "utf8"));
if (typeof parsed !== "object" || parsed === null || typeof parsed.url !== "string") {
  throw new Error("VIDEO.json must be an object with a string url field");
}
mkdirSync(outDir, { recursive: true });
copyFileSync(src, join(outDir, "VIDEO.json"));
console.log(`copied VIDEO.json to ${join(outDir, "VIDEO.json")}`);
