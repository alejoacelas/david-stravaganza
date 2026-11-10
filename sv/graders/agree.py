"""Two-rater agreement statistics: percent agreement, Cohen's kappa, Gwet's AC1.

Pairs where either rating is None are dropped (cascade stages a rater never reached).
`cats` fixes the category set, so AC1's chance term uses all possible categories.
"""
from collections import Counter

def agreement(a, b, cats):
    pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    n = len(pairs)
    if n == 0:
        return {"n": 0, "pct": None, "kappa": None, "ac1": None}
    po = sum(x == y for x, y in pairs) / n
    ca, cb = Counter(x for x, _ in pairs), Counter(y for _, y in pairs)
    pe_k = sum(ca[c] / n * cb[c] / n for c in cats)
    pi = {c: (ca[c] + cb[c]) / (2 * n) for c in cats}
    pe_g = sum(p * (1 - p) for p in pi.values()) / (len(cats) - 1)
    kappa = (po - pe_k) / (1 - pe_k) if pe_k < 1 else 1.0
    ac1 = (po - pe_g) / (1 - pe_g) if pe_g < 1 else 1.0
    return {"n": n, "pct": round(100 * po, 1), "kappa": round(kappa, 2), "ac1": round(ac1, 2)}
