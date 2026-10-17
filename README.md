# rational-ledger-recon

Reconciliation and anomaly detection for accounting that runs with no human in the loop.

When a firm runs its accounting with zero humans, every ledger entry posts without a person ever seeing it. That inverts the audit question: it's not "did someone approve this?" - nothing has a someone - it's "can every number on the ledger produce its evidence, and does the evidence agree?" This project is that check: a pre-posting gate between the bookkeeping engine and the ledger.

## What it does

For each proposed entry, the gate requires a source document (receipt, invoice, bank line) and checks the entry against it:

- **phantom_doc** (block): entry references a document that doesn't exist
- **amount_mismatch** (block): entry amount disagrees with the source document, with both figures named
- **vendor_mismatch** (block): the document belongs to a different vendor than the entry claims
- **duplicate_entry** (review): same vendor + amount + account already posted (double-posting)
- **no_source_doc** (review): entry with no evidence at all
- **negative_amount** (review): refunds and adjustments, flagged for confirmation
- **uncategorized** (info): posted without an account

Blocks and review items come back with the exact figures and the conflicting evidence, so the discrepancy is a finding, not a mystery.

## Demo

```
python3 -m ledgerrecon.cli
```

```
entries: 7 | post: 3 | needs_review: 2 | rejected: 2 ($264.00) | unmatched docs: 1
  [review] E-904 (WeWork $1,250.00): duplicate_entry: same vendor+amount+account as entry E-903 (double-post?)
  [block] E-905 (Figma $54.00): amount_mismatch: entry $54.00 != doc DOC-204 $45.00
  [block] E-906 (Office Depot $210.00): phantom_doc: references DOC-299, which does not exist
  [review] E-907 (Misc consulting $4,000.00): no_source_doc: entry has no source document ($4,000.00 unsupported)
```

Three clean entries post. A double-posted rent invoice is flagged. A $9 typo against Figma's invoice is caught. An entry citing a document that doesn't exist is rejected. And $4,000 of "misc consulting" with no receipt goes to review instead of silently landing on the books.

## Run it

```bash
python3 -m pytest tests/ -q    # 9 tests
python3 -m ledgerrecon.cli     # demo reconciliation
```

## What's real vs mocked

| Component | Status |
|---|---|
| Document matching, mismatch and duplicate detection, verdict logic | Real |
| Demo ledger batch and source documents | Mocked (representative small-business expense data) |
| Bank feed / ERP connectors, OCR extraction | Not implemented |

## Design

[DESIGN.md](DESIGN.md): matching strategy, false-positive policy, scaling.
