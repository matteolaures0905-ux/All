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
