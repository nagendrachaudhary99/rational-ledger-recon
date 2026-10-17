# Design: the gate before anything posts

## The inversion

Human accounting assumes a person will notice a weird number. Zero-human accounting removes the person, so noticing has to be a system. Every source of error that a human would catch by eyeballing - a transposed digit, a receipt submitted twice, an expense with no receipt at all - has to be caught by a rule or it compounds silently until tax season.

## Severity tiers, and why

- **block** (entry cannot post): phantom documents, amount/vendor mismatches. These are provably wrong - the entry contradicts its own evidence.
- **review** (posts only after a look): duplicates, unsupported entries, negatives. Plausibly legitimate (a real second invoice, a legitimate refund) but indistinguishable from common errors. A zero-human system needs *some* human escalation path; this is it, and it's deliberately narrow.
- **info** (posts, noted): uncategorized. Real money, just unsorted.

The design goal: false positives are cheap (a review task), false negatives are expensive (wrong books). So the tiers err toward review, never toward silence.

## Matching strategy

Exact document-reference matching first - entries claim a doc ID, and we verify that claim. Fuzzy matching (vendor similarity, amount within tolerance, date windows) is the obvious next step for entries that arrive without a doc_ref; it's omitted here deliberately, because fuzzy matching writes its own false matches and a reconciliation tool must fail loud, not guess quiet.

## What the demo proves

A batch of seven representative entries: three clean, four exhibiting the four most common silent-ledger failures (double-post, transposition typo, phantom reference, no evidence). Each is caught at the right severity.

## Next steps

- Fuzzy doc-matching for unreferenced entries (vendor + amount + date window), with match confidence surfaced
- Bank-feed reconciliation (ledger vs statement lines)
- Recurrence detection for subscriptions (a charge that stops matching its monthly amount)
- Statement-period close checks (unmatched docs *and* unmatched entries both blocking close)
