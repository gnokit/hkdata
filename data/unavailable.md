# Unavailable topics memory

Machine-readable list: [`unavailable.jsonl`](unavailable.jsonl)  
(one JSON object per line).

## Schema

| Field | Meaning |
|-------|---------|
| `id` | Stable id (`exp-…`) |
| `topic` | What was asked / looked for |
| `reason` | Why it is not on data.gov.hk (or not as stated) |
| `proxy_datasets` | Closest dataset ids if any (may be empty) |
| `checked_at` | ISO date last confirmed |

## How agents should use it

1. Run `programs-search` then `catalog-search` as usual.
2. If the user question matches an **unavailable** topic (unemployment by
   district, 殺校名單, smart CCTV counts, Northern Metropolis ROI, pet-friendly
   restaurants, named scam parks, BR “how-to” steps, SmartPLAY table-tennis
   session availability, etc.):
   - **Say so clearly** — do not invent a dataset.
   - Offer **proxy_datasets** with an explicit caveat (proxy ≠ the asked series).
   - For procedures, redirect to GovHK / the department site.
3. Do **not** write a fake “success” program that only raises or returns empty
   for these topics; keep the memory here and in program `Quirks:` where a
   related function already exists.
4. Cross-cutting search traps: `programs/_pitfalls.md`.

