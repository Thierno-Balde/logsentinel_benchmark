# BENCHMARK_REPORT — LogSentinel

Date de clôture technique : 2026-11-14.

## 1. Statut de livraison

LogSentinel est implémenté dans le dépôt public `Thierno-Balde/logsentinel_benchmark`, sur la branche dédiée `feature/initial-implementation` et dans la PR brouillon #1 vers `main`.

- Dépôt : `https://github.com/Thierno-Balde/logsentinel_benchmark`
- PR : `https://github.com/Thierno-Balde/logsentinel_benchmark/pull/1`
- Branche de travail : `feature/initial-implementation`
- `main` : non modifiée
- Fusion : non effectuée, aucune autorisation de merge n'a été donnée
- Dépendances : bibliothèque standard Python uniquement
- Environnement d'exécution : GitHub Actions, Python 3.12

## 2. Fonctionnalités terminées

- Lecture récursive des fichiers `.log` et `.txt`.
- Parsing de logs simples horodatés avec séparateur `T` ou espace.
- Parsing JSON Lines avec les champs courants `timestamp`/`time`/`ts`/`date`, `level`/`severity` et `message`/`msg`/`text`.
- Extraction de la date, du niveau et du message.
- Normalisation des niveaux `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` et `UNKNOWN`.
- Statistiques par niveau et par format.
- Gestion non bloquante des lignes corrompues et des dates invalides.
- Gestion non bloquante des fichiers UTF-8 invalides, reportés comme erreurs de fichier.
- Détection de rafales `ERROR`/`CRITICAL` sur une fenêtre configurable avec `--window`.
- Détection de groupes de messages répétés.
- Score indicatif de 0 à 100, avec ses composantes exposées dans le rapport.
- Export JSON et Markdown.
- CLI avec `--help`, `--path`, `--output` et `--window`.
- Rapports générés par CI et conservés dans `reports/`, ainsi que téléversés comme artefact CI.

## 3. Architecture livrée

- `logsentinel/parser.py` : lecture, parsing, dates, événements et erreurs de fichiers.
- `logsentinel/analyzer.py` : statistiques, rafales, répétitions et score.
- `logsentinel/report.py` : rendu JSON/Markdown et écriture des fichiers.
- `logsentinel/cli.py` : interface argparse.
- `logsentinel/__main__.py` : entrée `python -m logsentinel`.
- `tests/` : tests d'acceptation et tests de non-régression.
- `examples/` : journaux synthétiques entièrement fictifs.
- `reports/` : sorties générées par le runner CI.
- `.github/workflows/ci.yml` : tests, génération, vérification et upload des rapports.

## 4. Commandes et actions réellement exécutées

Toutes les commandes applicatives ci-dessous ont été exécutées par GitHub Actions, pas sur le VPS d'orchestration.

```text
python -m unittest discover -s tests -v
python -m logsentinel --path examples/sample.log --output ci-reports/sample --window 60
python -m logsentinel --path examples/sample_jsonl.txt --output ci-reports/jsonl --window 60
test -s ci-reports/sample.json
test -s ci-reports/sample.md
test -s ci-reports/jsonl.json
test -s ci-reports/jsonl.md
```

Actions GitHub réalisées :

1. Création du dépôt public dédié.
2. Création de `feature/initial-implementation` depuis `main`.
3. Écriture des tests avant l'implémentation.
4. Ouverture de la PR brouillon #1.
5. Lecture des logs CI, corrections et relances.
6. Téléchargement et inspection de l'artefact `logsentinel-reports`.
7. Ajout des rapports générés dans `reports/` via l'API GitHub.

## 5. Runs GitHub Actions et résultats

| Run | SHA testé | Résultat | Preuve principale |
|---|---|---|---|
| `43595525507` | `7db3e36b5e97b5d8e52bc8a8f1575279113e818c` | Échec TDD attendu | `ModuleNotFoundError` avant l'implémentation |
| `43596053219` | `b2827cf1d6d75b41e94aff69ceab2357134b60c2` | Échec | Regex mal encodée dans le premier payload GitHub |
| `43596202572` | `d29315fce3379a9e611a75e8b15e1ea53e4c544b` | Échec | Assertion CLI incorrecte, code fonctionnel mais test trop exigeant |
| `43596265740` | `7f422e4419eda99e0bab4f270c7ddcbbb7bf205e` | Succès | 11 tests, génération des quatre rapports |
| `43596386927` | `05f40406b2bc0522d0d26a231503d012bf6fc72f` | Échec d'auto-audit volontaire | Trois régressions révélées par les nouveaux tests |
| `43596540628` | `369cf19c38ce6126c7b1fdc24c3ca4fd1c293b10` | Succès final de l'auto-audit | 15 tests, rapports générés et uploadés |
| `43596607024` | `34c638120a202c03ac83901b6fa44276731084b3` | Succès | Rapports présents dans le dépôt et artefact CI valide |

Les annotations non bloquantes observées concernent la migration future de `ubuntu-latest` et la dépréciation Node.js 20 utilisée par des actions GitHub maintenues. Elles n'ont pas affecté l'exécution du job Python.

## 6. Tests finaux

Run final d'auto-audit : `43596540628`.

- **15 tests réussis**
- **0 test échoué**
- Parsing simple : couvert
- Parsing JSON Lines : couvert
- Statistiques de gravité : couvertes
- Rafales d'erreurs : couvertes
- Répétitions : couvertes
- Dates invalides : couvertes
- Dossier vide : couvert
- Chemin inexistant : couvert
- Encodage invalide : couvert
- JSON et Markdown : couverts
- CLI et `--help` : couverts
- Dates séparées par espace : test de non-régression ajouté
- Fuseaux horaires mélangés : test de non-régression ajouté
- Erreur CLI sur chemin absent : test de non-régression ajouté
- Échappement Markdown des backticks : test de non-régression ajouté

## 7. Erreurs rencontrées et corrections

1. **Implémentation absente au premier run.** C'était le rouge TDD attendu ; le package a ensuite été ajouté.
2. **Regex mal encodée dans le premier commit d'implémentation.** Le payload GitHub avait doublé les antislashs ; la regex a été réécrite et le run suivant a isolé l'erreur.
3. **Assertion CLI erronée.** Le test cherchait `30` dans la sortie standard alors que `--window` devait être vérifié dans le rapport. Le test a été corrigé pour lire la configuration JSON.
4. **Timestamp séparé par un espace mal découpé.** Le parser reconnaît maintenant `2026-11-14 10:00:00` comme une date complète.
5. **Chemin CLI inexistant remontant une traceback brute.** La CLI transforme maintenant l'erreur en erreur argparse propre avec code 2.
6. **Backticks provenant d'un log pouvant casser le Markdown.** Les valeurs injectées dans les codes Markdown sont échappées.
7. **Comparaison de fenêtres de rafale basée sur des chaînes.** La déduplication des rafales utilise maintenant les objets datetime, ce qui est correct avec des offsets différents.

## 8. Résultats de l'auto-audit

Les faiblesses raisonnablement corrigeables ont été traitées : formats de date courants, gestion CLI des chemins invalides, échappement Markdown et comparaison temporelle indépendante de la représentation textuelle du fuseau.

Le test d'auto-audit a d'abord été poussé seul et a produit le run rouge `43596386927`. Après correction, le run `43596540628` est passé avec 15 tests réussis. Cela prouve que les corrections n'ont pas seulement été écrites : elles ont été exercées par CI.

## 9. Méthode de score

Le score est déterministe et indicatif :

- 0 à 20 points pour le ratio de lignes invalides ;
- 0 à 40 points pour le ratio `ERROR` + `CRITICAL` ;
- 0 à 20 points pour les groupes de rafales ;
- 0 à 20 points pour les groupes de répétitions ;
- plafonnement à 100.

Le score n'est pas une probabilité d'incident et ne remplace ni un SIEM ni une investigation humaine.

## 10. Limites techniques

- Le parsing vise deux formats génériques et ne couvre pas tous les formats propriétaires.
- Les alias de champs JSON sont limités aux clés documentées dans le README.
- La détection de répétitions normalise les espaces mais ne fait pas de clustering sémantique.
- Les rafales exigent des dates valides ; les événements sans date restent comptés mais ne peuvent pas entrer dans une fenêtre temporelle.
- Les fichiers UTF-8 invalides sont signalés comme erreurs de fichier, sans tentative de deviner un encodage.
- Le score est un indicateur de triage, sans calibration sur un jeu d'incidents réels.
- Aucun stockage persistant, streaming, rotation de fichiers, corrélation multi-source ou interface graphique n'est inclus.
- Les performances n'ont pas été benchmarkées sur des fichiers de plusieurs gigaoctets.

## 11. Sources consultées

- Python `datetime.fromisoformat` : `https://docs.python.org/3/library/datetime.html#datetime.datetime.fromisoformat`
- Python `json` et option JSON Lines : `https://docs.python.org/3/library/json.html`
- Spécification JSON Lines : `https://jsonlines.org/`
- NIST SP 800-92, *Guide to Computer Security Log Management* : `https://csrc.nist.gov/pubs/sp/800/92/final`
- NIST Log Management overview : `https://csrc.nist.gov/Projects/log-management`

Les sources Python ont guidé le traitement des dates ISO 8601 et du JSON ligne par ligne. NIST a servi de garde-fou de périmètre : LogSentinel est un outil de triage et non une solution complète de gestion ou de surveillance de journaux.

## 12. Interventions humaines et durée

- Intervention humaine requise pendant l'exécution : **aucune**.
- Les décisions de conception, les corrections, les tests et les vérifications ont été exécutés par l'agent via l'API GitHub et GitHub Actions.
- Autorisation préalable de fusion : non fournie ; la PR reste donc en brouillon.
- Durée mesurable entre la création du dépôt (`2026-11-14T12:32:37Z`) et la fin du run `43596607024` (`2026-11-14T12:48:33Z`) : **956 secondes, soit 15 min 56 s**.

## 13. Conclusion honnête

La condition technique de réussite est satisfaite : dépôt dédié, branche isolée, code complet, tests automatisés verts, rapports réellement générés et vérifiés, auto-audit documenté, limites explicites et aucune modification de `main`.

La seule étape volontairement non réalisée est la fusion de la PR, qui reste soumise à une autorisation explicite.