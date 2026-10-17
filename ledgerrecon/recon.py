"""Match ledger entries to source documents; flag what must not post silently.

Zero-human accounting inverts the usual audit question. It is not 'did a
human approve this?' - nothing has a human. It is 'can every number on the
ledger produce its evidence, and does the evidence agree?' This module is
that check.
"""
from .models import EntryVerdict, Finding


def _norm(s: str) -> str:
    return " ".join(s.lower().split())


def reconcile(entries, docs, dup_window_days=None):
    by_id = {d.doc_id: d for d in docs}
    verdicts = []
    posted_keys = {}

    for e in entries:
        findings = []
        doc = by_id.get(e.doc_ref) if e.doc_ref else None

        if not e.doc_ref:
            findings.append(Finding("no_source_doc", "review", e.entry_id,
                                    f"entry has no source document (${e.amount:,.2f} unsupported)", e.amount))
        elif doc is None:
            findings.append(Finding("phantom_doc", "block", e.entry_id,
                                    f"references {e.doc_ref}, which does not exist", e.amount))
        else:
            if _norm(doc.vendor) != _norm(e.vendor):
                findings.append(Finding("vendor_mismatch", "block", e.entry_id,
                                        f"doc {doc.doc_id} is from {doc.vendor}, entry says {e.vendor}", e.amount))
            if abs(doc.amount - e.amount) > 0.01:
                findings.append(Finding("amount_mismatch", "block", e.entry_id,
                                        f"entry ${e.amount:,.2f} != doc {doc.doc_id} ${doc.amount:,.2f}", abs(doc.amount - e.amount)))

        key = (_norm(e.vendor), round(e.amount, 2), e.account)
        if key in posted_keys:
            findings.append(Finding("duplicate_entry", "review", e.entry_id,
                                    f"same vendor+amount+account as entry {posted_keys[key]} (double-post?)", e.amount))
        else:
            posted_keys[key] = e.entry_id

        if e.amount < 0:
            findings.append(Finding("negative_amount", "review", e.entry_id,
                                    "negative amount (refund/adjustment - confirm it's intended)", e.amount))
        if not e.account or e.account == "uncategorized":
            findings.append(Finding("uncategorized", "info", e.entry_id, "no account assigned"))

        if any(f.severity == "block" for f in findings):
            v = "REJECTED"
        elif any(f.severity == "review" for f in findings):
            v = "NEEDS_REVIEW"
        else:
            v = "POST"
        verdicts.append(EntryVerdict(entry=e, verdict=v, findings=findings))

    summary = {
        "entries": len(verdicts),
        "post": sum(1 for v in verdicts if v.verdict == "POST"),
        "needs_review": sum(1 for v in verdicts if v.verdict == "NEEDS_REVIEW"),
        "rejected": sum(1 for v in verdicts if v.verdict == "REJECTED"),
        "rejected_amount": round(sum(v.entry.amount for v in verdicts if v.verdict == "REJECTED"), 2),
        "unmatched_docs": len([d for d in docs if d.doc_id not in {e.doc_ref for e in entries}]),
    }
    return verdicts, summary
