"""Shared Anthropic client: disk cache, cost ledger, hard budget cap.

Every model call in this project goes through call(). Identical requests are
served from runs/cache, so reruns are free. Costs are estimated with the
conservative rates below and appended to runs/ledger.jsonl; once the ledger
total reaches BUDGET_USD, call() raises BudgetExceeded.
"""
import hashlib, json, os, threading, time
from pathlib import Path
from dotenv import load_dotenv
import anthropic

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
os.environ.pop("ANTHROPIC_BASE_URL", None)  # Claude Code sets a proxy; scripts use the API directly

BUDGET_USD = float(os.environ.get("SV_BUDGET_USD", "200"))
# USD per million tokens (input, output). Deliberately high so the cap errs safe.
RATES = {"claude-opus-5-5": (15.0, 75.0), "claude-haiku-5-5": (1.0, 5.0), "claude-sonnet-5-5": (3.0, 15.0)}
OPUS, HAIKU = "claude-opus-5-5", "claude-haiku-5-5"

CACHE = ROOT / "runs" / "cache"; CACHE.mkdir(parents=True, exist_ok=True)
LEDGER = ROOT / "runs" / "ledger.jsonl"
_lock = threading.Lock()
_client = anthropic.Anthropic(max_retries=6)

class BudgetExceeded(RuntimeError):
    pass

def spent() -> float:
    if not LEDGER.exists():
        return 0.0
    return sum(json.loads(l)["usd"] for l in LEDGER.read_text().splitlines() if l.strip())

def call(prompt: str, *, system: str = "", model: str = OPUS, max_tokens: int = 8000,
         effort: str | None = None, tag: str = "", seed: int = 0, cache_system: bool = True) -> str:
    """Return the text of one model reply. `seed` only varies the cache key, for repeat runs."""
    key = hashlib.sha256(json.dumps([prompt, system, model, max_tokens, effort, seed]).encode()).hexdigest()
    f = CACHE / f"{key}.json"
    if f.exists():
        return json.loads(f.read_text())["text"]
    with _lock:
        if spent() >= BUDGET_USD:
            raise BudgetExceeded(f"ledger at ${spent():.2f} >= cap ${BUDGET_USD}")
    kw = dict(model=model, max_tokens=max_tokens, messages=[{"role": "user", "content": prompt}])
    if system:
        kw["system"] = [{"type": "text", "text": system, **({"cache_control": {"type": "ephemeral"}} if cache_system else {})}]
    if effort:
        kw["output_config"] = {"effort": effort}
    t = time.time()
    with _client.messages.stream(**kw) as s:
        r = s.get_final_message()
    text = "".join(b.text for b in r.content if b.type == "text")
    u = r.usage
    rin, rout = RATES.get(model, RATES[OPUS])
    inp = (u.input_tokens + (u.cache_creation_input_tokens or 0) * 1.25 + (u.cache_read_input_tokens or 0) * 0.1)
    usd = inp / 1e6 * rin + u.output_tokens / 1e6 * rout
    f.write_text(json.dumps({"text": text, "model": model, "tag": tag}))
    with _lock, LEDGER.open("a") as lf:
        lf.write(json.dumps({"tag": tag, "model": model, "usd": round(usd, 4), "in": u.input_tokens,
                             "out": u.output_tokens, "secs": round(time.time() - t, 1)}) + "\n")
    return text

def parse_json(text: str):
    """Extract the first JSON object or array from a model reply."""
    s = text.strip()
    if "```" in s:
        parts = s.split("```")
        for p in parts[1::2]:
            p = p.split("\n", 1)[1] if p.lstrip().startswith(("json", "JSON")) else p
            try:
                return json.loads(p)
            except Exception:
                pass
    for open_, close in (("{", "}"), ("[", "]")):
        i, j = s.find(open_), s.rfind(close)
        if i != -1 and j > i:
            try:
                return json.loads(s[i:j + 1])
            except Exception:
                continue
    raise ValueError("no JSON found in reply: " + s[:300])
