# Générateur de lyric video TikTok (1080x1920)

Mots qui apparaissent un par un avec effet pop, mot en cours surligné, mots *mis en avant* dans un encadré coloré,
fond dégradé animé qui change de couleur à chaque ligne, zoom et flash sur les basses, formes flottantes, barre de progression.

## Utilisation avec ton son

1. Mets ton fichier audio (acheté ou extrait légalement) dans ce dossier, par ex. `son.mp3`.
2. Copie `paroles_demo.json` en `paroles.json` et remplace le texte et les temps (en secondes) par ceux de l'extrait choisi.
   Tu peux aussi utiliser un fichier `.srt`.
   - Un mot entre `*ÉTOILES*` est mis en avant.
   - Optionnel : `"words": [t1, t2, ...]` pour fixer l'instant exact de chaque mot.
3. Lance :

```bash
python3 make_video.py --lyrics paroles.json --audio son.mp3 --start 45 --duration 60 \
  --title "La vie qu'on mène" --artist "Ninho" --out ma_video.mp4
```

`--start` = seconde du morceau où commence l'extrait. Les temps des paroles sont **relatifs à ce début**.

Prérequis : `python3`, `numpy`, `Pillow`, `ffmpeg`.

## Style « cartoon » (`make_cartoon.py`)

Scènes dessinées en niveaux de gris avec un accent jaune-orangé (rue, mur de briques, parc, salle avec lampe,
scène de théâtre, toit la nuit), personnage original animé (casquette jaune, sweat à capuche) dont la bouche suit la voix,
paroles en karaoké en haut (gris → blanc), mot fort en grand en orange, zoom de caméra et coupe à chaque ligne.

```bash
python3 make_cartoon.py --lyrics paroles.json --audio son.mp3 --start 45 --duration 60 --out ma_video.mp4
```

Pour imposer un décor à une ligne : ajoute `"scene": "stage"` (street, wall, park, room, stage, roof).
Police : Oswald (licence SIL OFL, voir `fonts/OFL-Oswald.txt`).

## Extrait de 40,7 s : modèle minuté

`paroles_a_remplir.json` contient 20 emplacements calés sur la voix. Chaque ligne de l'extrait est coupée en deux
(à la virgule), donc 10 lignes donnent 20 emplacements. Remplis le champ `"text"` puis lance :

```bash
python3 make_cartoon.py --lyrics paroles_a_remplir.json --audio son_extrait.m4a --duration 40.7 --out ma_video.mp4
```
