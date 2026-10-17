"""CLI: reconcile the bundled ledger batch against source docs."""
import json
import os
from .models import LedgerEntry, SourceDoc
from .recon import reconcile

DATA = os.path.join(os.path.dirname(__file__), "..", "data")


def _load(name):
    with open(os.path.join(DATA, name)) as f:
        return json.load(f)


def main(argv=None):
    docs = [SourceDoc(**d) for d in _load("documents.json")]
    entries = [LedgerEntry(**e) for e in _load("entries.json")]
    verdicts, summary = reconcile(entries, docs)
    print(f"entries: {summary['entries']} | post: {summary['post']} | needs_review: {summary['needs_review']} | "
          f"rejected: {summary['rejected']} (${summary['rejected_amount']:,.2f}) | unmatched docs: {summary['unmatched_docs']}")
    for v in verdicts:
        for f in v.findings:
            print(f"  [{f.severity}] {v.entry.entry_id} ({v.entry.vendor} ${v.entry.amount:,.2f}): {f.code}: {f.message}")
    return 0 if summary["rejected"] == 0 and summary["needs_review"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
