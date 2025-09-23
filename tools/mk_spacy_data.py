import json, sys, spacy
from spacy.tokens import DocBin

def convert(in_path, out_path, lang="en"):
    nlp = spacy.blank(lang)
    db = DocBin(store_user_data=True)
    with open(in_path, "r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            text = rec["text"]
            ents = rec.get("entities", [])
            doc = nlp.make_doc(text)
            spans = []
            for s, e, label in ents:
                span = doc.char_span(s, e, label=label, alignment_mode="expand")
                if span is None:
                    raise ValueError(f"Span None for: {text[s:e]!r} @ {s}-{e}")
                spans.append(span)
            doc.ents = spans
            db.add(doc)
    db.to_disk(out_path)
    print(f"Wrote {out_path}")

if __name__ == "__main__":
    convert("data/train.jsonl", "data/train.spacy")
    convert("data/dev.jsonl",   "data/dev.spacy")
