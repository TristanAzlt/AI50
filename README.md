# AI50 - Modèle NER avec spaCy

Ce projet utilise spaCy pour entraîner un modèle de reconnaissance d'entités nommées (NER).

## Prérequis

- Python 3.9+
- pip (gestionnaire de paquets Python)

## Installation

1. Cloner le repository :

```bash
git clone https://github.com/TristanAzlt/AI50.git
cd AI50
```

2. Créer un environnement virtuel et l'activer :

```bash
python -m venv venv
# Sur macOS/Linux :
source venv/bin/activate
# Sur Windows :
.\venv\Scripts\activate
```

3. Installer les dépendances :

```bash
pip install -r requirements.txt
```

## Structure des données

Le projet attend les données d'entraînement dans le format suivant :

- `data/train.jsonl` : Données d'entraînement
- `data/dev.jsonl` : Données de validation
- `data/train_spans.jsonl` : Annotations des spans pour l'entraînement
- `data/dev_spans.jsonl` : Annotations des spans pour la validation

## Préparation des données

Pour convertir les données au format spaCy :

```bash
python tools/mk_spacy_data.py
```

## Entraînement du modèle

Pour entraîner le modèle avec spaCy :

```bash
python -m spacy train config.cfg --output ./models --paths.train ./data/train.spacy --paths.dev ./data/dev.spacy
```

Le modèle entraîné sera sauvegardé dans le dossier `models/`. Vous trouverez deux versions :

- `model-best` : La meilleure version du modèle pendant l'entraînement
- `model-last` : La dernière version du modèle

Pour tester le modèle avec un exemple :

```bash
python main.py
```

## Test du modèle

Pour tester le modèle :

```bash
python test_ner.py
```

## Configuration

Le fichier `config.cfg` contient la configuration du modèle spaCy. Vous pouvez ajuster les paramètres selon vos besoins :

- Taille du batch
- Nombre d'époques
- Taux d'apprentissage
- etc.
