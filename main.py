# main.py — test rapide: NER + normalisation + rattachement + topologie 

import re, json
from pathlib import Path
import spacy

# ---------- 0) ta phrase de test ----------
PHRASE = "Make a circuit with a 5V battery and a 1kΩ resistor plus an LED to GND."

# ---------- 1) load modèle ----------
def load_nlp():
    p = Path("models/model-best")
    return spacy.load(str(p)) if p.exists() else spacy.load("en_core_web_sm")
nlp = load_nlp()

# ---------- 2) helpers de normalisation ----------
def norm_voltage(txt: str) -> str:
    m = re.search(r"(\d+(?:\.\d+)?)\s*(v|volt)s?$", txt, re.I)
    if not m:
        nums = re.findall(r"\d+(?:\.\d+)?", txt)
        return (nums[0] if nums else "5") + "V"
    return f"{m.group(1)}V"

def norm_resistance(txt: str) -> str:
    t = txt.strip().lower().replace(" ", "").replace("Ω", "ohm")
    m = re.match(r"(\d+(?:\.\d+)?)(k|m|mega)?(ohm)?", t)
    if not m:
        return txt.strip().replace("Ω", " ohm")
    num = float(m.group(1))
    pref = (m.group(2) or "")
    if pref == "k": num *= 1e3
    elif pref == "m": num *= 1e-3
    elif pref == "mega": num *= 1e6
    if abs(num - round(num)) < 1e-9:
        num = int(round(num))
    return f"{num} ohm"

def is_voltage_text(txt: str) -> bool:
    return bool(re.search(r"(?:\d|\.)\s*(v|volt)s?$", txt.strip(), re.I))
def is_ohm_text(txt: str) -> bool:
    return bool(re.search(r"(?:\d|\.)\s*(ohm|Ω|kΩ|MΩ|kohm|mohm)", txt.strip(), re.I))

# ---------- 3) rattacher valeurs/unités aux composants ----------
def attach_values(ents):
    # ents = [{"text","label","start","end"}]
    ents = sorted(ents, key=lambda e: e["start"])
    comps = [e for e in ents if e["label"] in ("POWER_SUPPLY","RESISTOR","LED")]
    vals  = [e for e in ents if e["label"] in ("VALUE","UNIT")]

    # fusion VALUE + UNIT s'ils sont collés
    fused = []
    i = 0
    while i < len(vals):
        v = vals[i]
        if v["label"] == "VALUE" and i+1 < len(vals) and vals[i+1]["label"]=="UNIT" \
           and 0 <= vals[i+1]["start"] - v["end"] <= 2:
            fused.append({"text": v["text"] + " " + vals[i+1]["text"], "start": v["start"], "end": vals[i+1]["end"]})
            i += 2
        else:
            fused.append({"text": v["text"], "start": v["start"], "end": v["end"]})
            i += 1

    # init
    for c in comps:
        c["kind"] = {"POWER_SUPPLY":"VDC","RESISTOR":"RES","LED":"LED"}[c["label"]]
        c["value"] = None
        c["pins"]  = ["+","-"] if c["kind"]=="VDC" else (["1","2"] if c["kind"]=="RES" else ["A","K"])

    # pour chaque valeur, choisir le composant cible le plus proche & cohérent
    for v in fused:
        target = "VDC" if is_voltage_text(v["text"]) else ("RES" if is_ohm_text(v["text"]) else None)
        cand = [c for c in comps if (target is None) or (c["kind"] == target)]
        if not cand: 
            continue
        nearest = min(cand, key=lambda c: min(abs(v["start"]-c["start"]), abs(v["end"]-c["end"])))
        if nearest["kind"] == "VDC":
            nearest["value"] = norm_voltage(v["text"])
        elif nearest["kind"] == "RES":
            nearest["value"] = norm_resistance(v["text"])
    return comps

# ---------- 4) inférer une topologie simple + JSON ----------
def build_design(comps, text):
    # source en premier si présente
    ordered = sorted(comps, key=lambda c: c["start"])
    src = [c for c in ordered if c["kind"]=="VDC"]
    if src:
        ordered = src + [c for c in ordered if c["kind"]!="VDC"]

    # IDs
    counters = {"VDC":0,"RES":0,"LED":0}
    for c in ordered:
        counters[c["kind"]] += 1
        c["id"] = {"VDC":"V","RES":"R","LED":"D"}[c["kind"]] + str(counters[c["kind"]])

    # connexions: série par défaut
    connections = []
    ids = [c["id"] for c in ordered]
    net_idx = 1
    for a, b in zip(ids, ids[1:]):
        n = f"N{net_idx}"; net_idx += 1
        pa = "+" if a.startswith("V") else ("2" if a.startswith("R") else "A")
        pb = "1" if b.startswith("R") else ("A" if b.startswith("D") else "+")
        connections += [{"from": f"{a}:{pa}", "to": n}, {"from": n, "to": f"{b}:{pb}"}]

    # ground si mentionné
    if re.search(r"\b(gnd|ground|masse)\b", text, re.I):
        for c in ordered:
            if c["kind"] == "LED":
                connections.append({"from": f"{c['id']}:K", "to": "GND"})
        for c in ordered:
            if c["kind"] == "VDC":
                connections.append({"from": f"{c['id']}:-", "to": "GND"})

    design = {
        "components": [{"id":c["id"], "kind":c["kind"], "value":c["value"], "pins":c["pins"]} for c in ordered],
        "connections": connections
    }
    return design

# ---------- 5) run ----------
def run(text: str):
    doc = nlp(text)
    ents = [{"text":e.text,"label":e.label_,"start":e.start_char,"end":e.end_char} for e in doc.ents]
    comps = attach_values(ents)
    design = build_design(comps, text)

    print("# Input:")
    print(text)
    print("\n")
    print("--------------------------------")
    print("\n# Entities:")
    for e in doc.ents:
        print(f"{e.text:12} -> {e.label_}")
    print("\n# Components (attached & normalized):")
    for c in design["components"]:
        print(c)
    print("\n# Connections:")
    for c in design["connections"]:
        print(c)
    print("\n# DESIGN JSON:")
    print(json.dumps(design, indent=2))

if __name__ == "__main__":
    run(PHRASE)
