# Framework de chiffrement (SSAD TP1)

Travail pratique du cours SSAD, USTHB 2026-2027. Python 3, bibliothèque standard uniquement.

Ce dépôt contient une interface de messagerie entre une entité A (émetteur) et
une entité B (récepteur), ainsi que les implémentations des chiffrements de la
partie 2.

## Lancement

```
python app.py
python tests_partie2.py
```

## Contenu

| Fichier | Rôle |
|---------|------|
| `partie2/__init__.py` | Package Python de la partie 2 |
| `partie2/ciphers.py` | Façade commune pour César, Hill, Playfair et le canal |
| `partie2/cesar.py` | Chiffrement de César |
| `partie2/hill.py` | Chiffrement de Hill |
| `partie2/playfair.py` | Chiffrement de Playfair |
| `app.py` | Navigation Tkinter et pages de messagerie |
| `login.py` | Page de connexion CRYPTOLINK |
| `database.py` | Accès MySQL/MariaDB, comptes, messages et notifications |
| `tests_partie2.py` | Tests des chiffrements |
| `code_interface.pdf` | Code de la partie 1 |
| `code_chiffrements.pdf` | Code de la partie 2 avec explications |
| `report.pdf` | Rapport |

Les comptes, les messages et les notifications sont stockés dans la base MySQL/MariaDB
`crypto`. La connexion est configurable avec `CRYPTO_DB_HOST`, `CRYPTO_DB_PORT`,
`CRYPTO_DB_USER`, `CRYPTO_DB_PASSWORD` et `CRYPTO_DB_NAME`.

## Fonctionnement de l'interface

- La page de connexion identifie l'utilisateur et son rôle.
- La page **Envoyer un message** permet de choisir un contact, un algorithme, une clé et le sens pour César.
- Le message doit contenir au moins une lettre.
- La page **Boîte de réception** permet de consulter et déchiffrer les messages reçus.
- La page **Notifications** affiche les alertes de messages et de sécurité stockées en SQL.
- La page **Brute Force** est visible uniquement pour `Admin User` et simule un audit par dictionnaire.
- Les messages de succès et d'erreur sont affichés dans l'interface.
- Le canal contient le code binaire de l'algorithme, la direction pour César, la clé et le texte chiffré.

## Remarques

- Le code de l'algorithme est une métadonnée publique et ne constitue pas une protection cryptographique.
- Pour César, la clé est un entier ; les multiples de 52 sont refusés car ils ne modifient pas le message, tandis que 26 reste accepté.
- Pour Hill, la matrice doit être inversible modulo 26. La matrice identité est refusée car elle ne chiffre pas réellement le message.
- Pour Playfair, la clé doit contenir uniquement des lettres ASCII sans espace ni ponctuation ; `J` est confondu avec `I` dans la grille.
- Une clé ne doit pas contenir le caractère `:`, utilisé comme séparateur du canal.
- Pour Hill, le canal contient uniquement les lettres chiffrées. Les positions des espaces et de la ponctuation sont mémorisées séparément, puis réutilisées après le déchiffrement.
- Playfair utilise maintenant la même méthode : le canal contient uniquement les lettres chiffrées, puis les positions mémorisées restaurent les espaces et la ponctuation après le déchiffrement.
- Playfair mémorise également les positions exactes des `X` ajoutés pendant la préparation des paires. Ainsi, un vrai `X` du message n'est pas supprimé par erreur lors du déchiffrement.
- Playfair mémorise les positions des `J` remplacés par `I` dans la grille 5x5, puis restaure ces `J` après le déchiffrement.
- Hill peut ajouter `X` pour compléter son dernier bloc, et Playfair peut ajouter `X` pour préparer ses paires. L'interface retire ces remplissages au déchiffrement ; un véritable `X` final peut donc nécessiter une convention supplémentaire.
- L'audit par dictionnaire est une simulation locale destinée au prototype ; il ne remplace pas un service de sécurité réel.
- Le message du canal utilise le format `code:direction:clé:chiffré` : `000` pour César, `001` pour Hill et `010` pour Playfair. La direction vaut `r` ou `l` uniquement pour César. La fonction `dechiffrement_automatique()` lit ces métadonnées et choisit automatiquement le déchiffrement.
- Les fichiers `code_interface.pdf` et `report.pdf` décrivent une version plus complète (mots de passe, HMAC, `tests.py`) dont les fichiers ne sont pas dans ce dépôt.

## Répartition du travail

| Membre | Tâche |
|--------|-------|
| 1 | Chiffrement de César |
| 2 | Chiffrement de Hill |
| 3 | Chiffrement de Playfair |
| 4 | Interface et tests |
