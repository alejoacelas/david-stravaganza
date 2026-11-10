"""G1 evidence checker: does each quoted span exist in the paper, and on the claimed page?

Mechanical, no model calls. Both paper and quote are normalized (NFKC, so ligatures like
"ﬁ" become "fi"; curly quotes and dashes unified; line-end hyphenation joined; remaining
hyphens dropped; "[p. N]" markers removed; whitespace collapsed; lowercase). An exact
substring hit scores 100. Otherwise rapidfuzz partial_ratio is taken over overlapping
windows of the paper (window = 2x quote length, stride = quote length), and the best
window is re-aligned to locate the match. A quote with an ellipsis ("..." or "[...]")
is split into fragments that must each match; its score is the lowest fragment score.

found = score >= THRESHOLD and no whole-word differences from the matched span
(word_edits empty; see _word_edits: small in-word character noise is tolerated, any digit
difference is not, so numbers_ok is part of it). THRESHOLD and MAX_WORD_EDITS were chosen in
sv/gold/g1_calibrate.py (see runs/gold/report.md); the score floor is not binding there, the
word-edit rule does the work.

check(paper_text, item) -> list of per-quote dicts
  {quote, found, score, numbers_ok, word_edits, page_found, page_claimed, page_claimed_ok}
`item` is a reviewer item with "evidence": [{"quote", "page"}], a single {"quote", "page"}
dict, or a bare quote string.
"""
import bisect, difflib, re, unicodedata
from functools import lru_cache
from rapidfuzz import fuzz

THRESHOLD = 70.0
MAX_WORD_EDITS = 0
PAGE_RE = re.compile(r"\[p\. (\d+)\]")
_TRANS = str.maketrans({"“": '"', "”": '"', "„": '"', "‘": "'", "’": "'", "´": "'", "`": "'",
                        "–": "-", "—": "-", "−": "-", "‐": "-", "‑": "-", "­": "", "…": "...",
                        " ": " ", "​": ""})


def _norm_with_map(text: str) -> tuple[str, list[int]]:
    """Normalize text; return it with, for each output char, the index of its source char."""
    out, idx = [], []
    text = re.sub(r"(\w)-[ \t]*\n\s*(\w)", r"\1\2", text)      # join line-end hyphenation
    for i, ch in enumerate(text):
        for c in unicodedata.normalize("NFKC", ch).translate(_TRANS).lower():
            if c == "-":
                continue
            if c.isspace() or c in "*_|":
                if out and out[-1] == " ":
                    continue
                c = " "
            out.append(c); idx.append(i)
    return "".join(out), idx


def norm(s: str) -> str:
    return _norm_with_map(PAGE_RE.sub(" ", s))[0].strip()


@lru_cache(maxsize=32)
def _prep(paper_text: str):
    """Normalized paper (page markers removed) plus normalized-char -> page lookup."""
    pages, starts, chunks, pos = [], [], [], 0
    parts = PAGE_RE.split(paper_text)
    # parts = [before, page1, text1, page2, text2, ...]
    seq = [(None, parts[0])] + [(int(parts[i]), parts[i + 1]) for i in range(1, len(parts) - 1, 2)]
    for pg, chunk in seq:
        n = norm(chunk)
        if not n:
            continue
        starts.append(pos); pages.append(pg if pg is not None else 1)
        chunks.append(n); pos += len(n) + 1
    return " ".join(chunks), starts, pages


def _page_at(starts, pages, pos):
    return pages[max(0, bisect.bisect_right(starts, pos) - 1)]


def _match(frag: str, P: str, starts, pages, page):
    """Best (score, start, end) of normalized fragment in normalized paper P.
    Among exact hits, prefer one on the claimed page (repeated figure axes, headers)."""
    i = P.find(frag)
    if i >= 0:
        if page is not None:
            j = i
            while j >= 0:
                if _page_at(starts, pages, j) == page:
                    return 100.0, j, j + len(frag)
                j = P.find(frag, j + 1)
        return 100.0, i, i + len(frag)
    L = len(frag)
    win, step = 2 * L, max(1, L)
    best = (0.0, 0)
    for s in range(0, max(1, len(P) - L + 1), step):
        sc = fuzz.partial_ratio(frag, P[s:s + win], score_cutoff=best[0])
        if sc > best[0]:
            best = (sc, s)
    if best[0] == 0:
        return 0.0, 0, 0
    s = best[1]
    al = fuzz.partial_ratio_alignment(frag, P[s:s + win])
    return best[0], s + al.dest_start, s + al.dest_end


def _word_edits(frag: str, P: str, a: int, b: int) -> list[str]:
    """Whole-word differences between the quote and the matched paper span.

    Character-level noise inside a word (OCR slips, a split word) is tolerated: a replaced
    block counts only if its joined characters differ substantially (rapidfuzz ratio < 80)
    or its digits differ at all (numbers must match exactly). Words present only in the
    quote count; paper-only tokens count unless they are 1-3 digits/punctuation (footnote
    markers). At the two ends of the quote, the quote's edge words are compared with the
    best-matching run of paper words, so context words outside the quote do not count.
    """
    if P[a:b] == frag:
        return []
    qa = frag.split()
    pa = P[max(0, a - 25):b + 25].split()
    ops = difflib.SequenceMatcher(None, qa, pa, autojunk=False).get_opcodes()
    while ops and ops[0][0] == "insert":
        ops = ops[1:]
    while ops and ops[-1][0] == "insert":
        ops = ops[:-1]
    digits = lambda x: re.sub(r"\D", "", x)
    bad = []
    for n, (t, i1, i2, j1, j2) in enumerate(ops):
        if t == "equal":
            continue
        q = "".join(qa[i1:i2])
        if t == "insert":
            w = "".join(pa[j1:j2])
            if not re.fullmatch(r"[\d\W]{1,3}", w):
                bad.append(f"+paper:{w}")
            continue
        if t == "delete":
            bad.append(f"-quote:{q}")
            continue
        # candidate paper runs: whole block, or at the quote's edges any suffix/prefix of it
        cands = [(j1, j2)]
        if n == 0:
            cands += [(k, j2) for k in range(j1, j2)]
        if n == len(ops) - 1:
            cands += [(j1, k) for k in range(j1 + 1, j2 + 1)]
        if n == 0 and n == len(ops) - 1:
            cands += [(k, m) for k in range(j1, j2) for m in range(k + 1, j2 + 1)]
        def cost(c):
            w = "".join(pa[c[0]:c[1]])
            ok_digits = digits(w) == digits(q) or (n == 0 and digits(w).endswith(digits(q))) \
                or (n == len(ops) - 1 and digits(w).startswith(digits(q)))
            r = fuzz.ratio(q, w)
            if n == 0 and w.endswith(q) or n == len(ops) - 1 and w.startswith(q):
                r = 100.0          # quote starts or ends mid-word
            return (ok_digits, r), w
        (ok_digits, r), w = max(cost(c) for c in cands)
        if not ok_digits:
            bad.append(f"digits:{q}->{w}")
        elif r < 80:
            bad.append(f"{q}->{w}")
    return bad


def check_quote(paper_text: str, quote: str, page: int | None = None) -> dict:
    P, starts, pages = _prep(paper_text)
    frags = [norm(f) for f in re.split(r"\[?\s*(?:\.\s*){3}\s*\]?|\[…\]|…", quote)]
    frags = [f for f in frags if len(f) >= 12] or [norm(quote)]
    scores, spans, edits = [], [], []
    for f in frags:
        sc, a, b = _match(f, P, starts, pages, page)
        scores.append(sc); spans.append((a, b))
        edits += _word_edits(f, P, a, b) if sc > 0 else ["no match"]
    score = min(scores)
    numbers_ok = not any(e.startswith("digits:") for e in edits)
    found = score >= THRESHOLD and numbers_ok and len(edits) <= MAX_WORD_EDITS
    pf = sorted({_page_at(starts, pages, p) for a, b in spans for p in (a, max(a, b - 1))}) if found else []
    return {"quote": quote, "found": found, "score": round(score, 1), "numbers_ok": numbers_ok,
            "word_edits": edits,
            "page_found": pf[0] if len(pf) == 1 else (pf or None),
            "page_claimed": page,
            "page_claimed_ok": (page in pf) if (found and page is not None) else None}


def check(paper_text: str, item) -> list[dict]:
    if isinstance(item, str):
        ev = [{"quote": item}]
    elif "evidence" in item:
        ev = item["evidence"] or []
    else:
        ev = [item]
    return [check_quote(paper_text, e.get("quote", ""), e.get("page")) for e in ev]
