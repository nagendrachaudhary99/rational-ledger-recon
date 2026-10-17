from dataclasses import dataclass, field


@dataclass
class SourceDoc:
    """A receipt/invoice/bank line: ground truth money evidence."""
    doc_id: str
    vendor: str
    amount: float
    date: str
    kind: str           # receipt | invoice | bank_line


@dataclass
class LedgerEntry:
    """A proposed or posted ledger entry. In a zero-human firm, entries
    like this post without a person ever looking - hence this tool."""
    entry_id: str
    vendor: str
    amount: float
    date: str
    account: str        # e.g. "meals", "software", "rent"
    doc_ref: str = ""   # source document the entry claims to post from


@dataclass
class Finding:
    code: str
    severity: str       # block | review | info
    entry_id: str
    message: str
    amount_at_stake: float = 0.0


@dataclass
class EntryVerdict:
    entry: LedgerEntry
    verdict: str        # POST | NEEDS_REVIEW | REJECTED
    findings: list = field(default_factory=list)
