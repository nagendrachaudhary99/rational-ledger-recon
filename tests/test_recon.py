import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ledgerrecon.cli import main
from ledgerrecon.models import LedgerEntry, SourceDoc
from ledgerrecon.recon import reconcile

DOCS = [
    SourceDoc("DOC-1", "Amazon Web Services", 100.00, "2026-10-03", "invoice"),
    SourceDoc("DOC-2", "Figma", 45.00, "2026-10-07", "invoice"),
    SourceDoc("DOC-3", "WeWork", 1250.00, "2026-10-01", "invoice"),
]


def entry(eid="E-1", vendor="Amazon Web Services", amount=100.00, account="software", ref="DOC-1"):
    return LedgerEntry(eid, vendor, amount, "2026-10-03", account, ref)


class TestMatching:
    def test_clean_posts(self):
        vs, s = reconcile([entry()], DOCS)
        assert vs[0].verdict == "POST" and s["post"] == 1

    def test_amount_mismatch_blocked(self):
        vs, s = reconcile([entry(amount=54.00, vendor="Figma", ref="DOC-2")], DOCS)
        assert vs[0].verdict == "REJECTED"
        assert any(f.code == "amount_mismatch" for f in vs[0].findings)
        assert s["rejected_amount"] == 54.00

    def test_vendor_mismatch_blocked(self):
        vs, _ = reconcile([entry(vendor="Figma", ref="DOC-1")], DOCS)
        assert vs[0].verdict == "REJECTED"
        assert any(f.code == "vendor_mismatch" for f in vs[0].findings)

    def test_phantom_doc_blocked(self):
        vs, _ = reconcile([entry(ref="DOC-99")], DOCS)
        assert vs[0].verdict == "REJECTED"
        assert any(f.code == "phantom_doc" for f in vs[0].findings)

    def test_no_source_review(self):
        vs, _ = reconcile([entry(ref="")], DOCS)
        assert vs[0].verdict == "NEEDS_REVIEW"

    def test_duplicate_posting_review(self):
        vs, _ = reconcile([entry("E-1"), entry("E-2")], DOCS)
        assert vs[0].verdict == "POST" and vs[1].verdict == "NEEDS_REVIEW"
        assert any(f.code == "duplicate_entry" for f in vs[1].findings)

    def test_unmatched_docs_counted(self):
        _, s = reconcile([entry()], DOCS)
        assert s["unmatched_docs"] == 2  # DOC-2, DOC-3 have no entries

    def test_uncategorized_info_only(self):
        vs, _ = reconcile([entry(account="uncategorized")], DOCS)
        assert vs[0].verdict == "POST"
        assert any(f.code == "uncategorized" for f in vs[0].findings)


class TestCLI:
    def test_demo_batch(self):
        # demo has a duplicate, an amount mismatch, a phantom doc, and an unsupported entry
        assert main() == 1
