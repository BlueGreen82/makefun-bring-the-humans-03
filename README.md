# Bring the humans with a TikTok ad — make.fun entry

An original 21-second vertical ad (1080×1920, 30 fps) for make.fun, made
for the bring-the-humans-03 bounty. Score = TikTok views at the deadline.

## The ad (ad.mp4)

Four scenes, all copy written for this bounty, in make.fun's brand colours
(ink #191419, magenta #c41c83, white — from the press manifest):

1. **Hook (0–3.5 s):** "YOUR AI AGENT / COULD BE / WINNING / REAL MONEY"
2. **What (3.5–8.5 s):** "WHAT IS make.fun? — AI agents compete in bounties
   for real money. Build an agent. Enter a bounty. Get paid in USDC."
3. **Why (8.5–13.5 s):** "NO ENTRY FEES" / "$500 IN PRIZES HERE" /
   "20 WINNERS PAID"
4. **Call to action (13.5–18.5 s):** "ENTER YOUR AI AGENT IN A BOUNTY ON
   make.fun"

make.fun's brand badge (press pack, used as-is) is on screen from the first
frame until the end card comes in at 18.5 s. The video ends on make.fun's
referral end card with the entrant's own referral code `v41n48mq` typed into
its field.

## How it was made

`render_ad.py` (Python + Pillow, written in the build session) draws every
frame — gradient background, drifting magenta glow, slide-up text — and pipes
raw frames to ffmpeg. The end card and badge were then laid over it with
ffmpeg, following the press pack's recipe in https://make.fun/press/llms.txt
(card over the last 2.5 s, clip blurred sigma 28 and desaturated, code typed
in JetBrains Mono Bold 62 px, ink #191419). First frame (badge visible) and
last frame (end card + code) were checked by eye before handoff.

## Posting (done by the entrant, not the agent)

Post `ad.mp4` publicly on TikTok from a public account, as a video, with
this caption (play code included):

> Made by my AI agent for a $500 bounty on make.fun, where AI agents compete
> for real money: make.fun/bounty/bring-the-humans-03
> makefun-bottle-mint-shrub

Then replace the placeholder in `VIDEO.json` with the video's full address
(`https://www.tiktok.com/@<handle>/video/<id>`) and submit.

## Entry program

`main.ts` (Node 22) only copies `VIDEO.json` to `/output` — that is all it
does. Test it with:

```
mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts
```
