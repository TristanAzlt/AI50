import spacy
nlp = spacy.load("models/model-best")

texts = [
    "Make a circuit with a 5V battery and a 330 ohm resistor plus an LED to ground.",
    "Use a 9V source then LED and 1kΩ resistor to GND."
]
for t in texts:
    doc = nlp(t)
    print("\n>", t)
    for ent in doc.ents:
        print(f"{ent.text:12} -> {ent.label_}")
