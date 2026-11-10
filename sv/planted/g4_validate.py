"""Validate G4 on hand-made detections (data/planted/g4_validation_cases.json) whose labels are known by construction."""
import json
from pathlib import Path
from sv import llm
from sv.planted.g4_score import score_variant, load_manifest, ROOT

def main():
    man = load_manifest()
    cases = json.load(open(ROOT / "data/planted/g4_validation_cases.json"))
    rows = []
    for c in cases:
        r = score_variant(c["variant_id"], c["items"], man, tag="g4-validate")
        lab = c["label"]
        if r["kind"] == "planted":
            rows.append({"case": c["case"], "kind": "planted", "det_ok": r["detected"] == lab["detected"],
                         "loc_ok": r["located"] == lab["located"], "got": [r["detected"], r["located"]], "want": [lab["detected"], lab["located"]],
                         "reason": r["items"][0]["reason"]})
        else:
            rows.append({"case": c["case"], "kind": "clean", "fa_ok": r["false_alarms"] == lab["false_alarms"],
                         "got": r["false_alarms"], "want": lab["false_alarms"], "reason": r["items"][0]["reason"]})
    pl = [r for r in rows if r["kind"] == "planted"]; cl = [r for r in rows if r["kind"] == "clean"]
    summary = {"n_cases": len(rows), "detection_acc": f"{sum(r['det_ok'] for r in pl)}/{len(pl)}",
               "location_acc": f"{sum(r['loc_ok'] for r in pl)}/{len(pl)}", "false_alarm_acc": f"{sum(r['fa_ok'] for r in cl)}/{len(cl)}",
               "overall_verdict_acc": f"{sum(r['det_ok'] for r in pl) + sum(r['fa_ok'] for r in cl)}/{len(rows)}"}
    out = ROOT / "runs/planted/g4_validation.json"; out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"summary": summary, "cases": rows}, indent=1))
    for r in rows:
        print(r)
    print(summary, "ledger total", round(llm.spent(), 2))

if __name__ == "__main__":
    main()
