import json, re, sys

def find_nth(text, sub, n=1, flags=re.IGNORECASE):
    matches = list(re.finditer(re.escape(sub), text, flags))
    return matches[n-1].span() if len(matches) >= n else None

def convert_record(rec):
    text = rec["text"]
    ents = []
    for span in rec["spans"]:
        sub = span["text"]
        label = span["label"]
        nth = int(span.get("nth", 1))
        pos = find_nth(text, sub, nth)
        if not pos:
            raise ValueError(f"'{sub}' (nth={nth}) introuvable dans: {text}")
        s, e = pos
        ents.append([s, e, label])
    return {"text": text, "entities": ents}

def main(inp, outp):
    with open(inp, encoding="utf-8") as fi, open(outp, "w", encoding="utf-8") as fo:
        for line in fi:
            if not line.strip():
                continue
            rec = json.loads(line)
            out = convert_record(rec)
            fo.write(json.dumps(out, ensure_ascii=False) + "\n")
    print(f"Wrote {outp}")

if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else "data/train_spans.jsonl"
    outp = sys.argv[2] if len(sys.argv) > 2 else "data/train.jsonl"
    main(inp, outp)
