# MESURIA – Analyse automatique de mensurations

MESURIA est une application web qui permet d’analyser automatiquement les mensurations d’une personne à partir d’une photo, en utilisant MediaPipe et OpenCV.  
L’utilisateur crée un compte, renseigne sa taille en cm, puis envoie une photo de face. L’application détecte la pose, calcule différentes distances sur le corps et les convertit en centimètres.

---

## Fonctionnalités

- Création de compte et connexion avec mot de passe hashé.
- Enregistrement de la **taille en cm** dans le profil utilisateur.
- Upload d’une photo (JPG/PNG), avec prévisualisation côté navigateur.
- Détection de la pose avec **MediaPipe Pose Landmarker**.
- Calcul des mensurations en pixels puis conversion en **cm** grâce à la taille réelle :
  - Épaule (largeur épaules)
  - Poitrine
  - Torse
  - Bras
  - Tour de taille
  - Longueur de jambe
- Interface moderne (HTML/CSS + animations) avec :
  - preview de l’image à gauche
  - cartes de mensurations à droite
- Sauvegarde de la date d’analyse dans la table `mensurations`.

---

## Technologies utilisées

- **Backend** : Python 3, Flask  
- **Pose / Vision** : MediaPipe Tasks (PoseLandmarker), OpenCV  
- **Base de données** : MySQL  
- **Frontend** : HTML5, CSS3, JavaScript, Font Awesome, Google Fonts  
- **Sécurité** : hash des mots de passe avec `werkzeug.security`

---

## Pré‑requis

- Python 3.x  
- MySQL  
- `pip` pour installer les dépendances

---

## Installation

1. Cloner le dépôt :

```bash
git clone <URL_DU_REPO>
cd mesuria
```

2. Créer un environnement virtuel (recommandé) :

```bash
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows
```

3. Installer les dépendances :

```bash
pip install -r requirements.txt
```

(Si tu n’as pas encore de `requirements.txt`, les principaux paquets sont : `flask`, `mysql-connector-python`, `opencv-python`, `mediapipe`.)

4. Créer la base de données MySQL `mesuria` et les tables principales :

```sql
CREATE DATABASE mesuria CHARACTER SET utf8mb4;

USE mesuria;

CREATE TABLE users (
  id_users INT AUTO_INCREMENT PRIMARY KEY,
  Nom VARCHAR(100),
  Prenom VARCHAR(100),
  email VARCHAR(255) UNIQUE,
  Mot_de_passe VARCHAR(255),
  Taille_cm INT,
  Date_de_creation DATETIME
);

CREATE TABLE mensurations (
  id_mensuration INT AUTO_INCREMENT PRIMARY KEY,
  date_analyse DATETIME,
  id_users INT,
  FOREIGN KEY (id_users) REFERENCES users(id_users)
);
```

5. Configurer la connexion MySQL dans `app.py` si besoin :

```python
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="mesuria",
    )
    return conn
```

6. Lancer l’application :

```bash
python app.py
```

L’application est disponible sur `http://127.0.0.1:5000`.

---

## Utilisation

1. **Inscription** (`/register`)  
   Renseigner nom, prénom, email, mot de passe et **taille en cm**.

2. **Connexion** (`/login`).

3. **Analyse de mensurations** (`/mensurations`)  
   - Lire le guide (position, vêtements, éclairage).  
   - Cliquer sur **Upload ma photo** et choisir une photo de face.  
   - Vérifier la prévisualisation à gauche.  
   - Cliquer sur **Lancer l’analyse**.

4. Après analyse :
   - Les cartes de résultats s’affichent à droite avec les mesures en **cm**.  
   - La date d’analyse est enregistrée dans la table `mensurations`.

5. **Déconnexion** : lien MESURIA (logout) en haut de page.

---

## Détails techniques – Conversion pixels → cm

MediaPipe fournit les coordonnées des points du corps en valeurs normalisées.  
MESURIA :

1. Convertit ces coordonnées en **pixels** avec la taille de l’image.  
2. Calcule la **taille en pixels** entre le nez et la cheville (approximation de la hauteur de la personne).  
3. Lit la taille réelle `Taille_cm` depuis la BDD.  
4. Calcule un facteur d’échelle :

\[
cm\_par\_px = \frac{\text{taille\_réelle\_cm}}{\text{taille\_pixels}}
\]

5. Convertit chaque mesure :

\[
\text{mesure\_cm} = \text{mesure\_px} \times cm\_par\_px
\]

Les valeurs obtenues sont approximatives et dépendent de la photo (position, angle, perspective).

---

## Structure des fichiers (simplifiée)

- `app.py` : application Flask et logique d’analyse.  
- `templates/`  
  - `Accueil.html` – page d’accueil  
  - `compte.html` – inscription  
  - `seconnecter.html` – connexion  
  - `Mensurations.html` – interface d’analyse  
- `static/`  
  - `style.css` – styles globaux  
  - `uploads/` – photos uploadées

---

## Limitations et pistes d’amélioration

- Nécessite une photo de face avec la personne entière visible.  
- Conversion en cm approximative (dépend de la pose et de la perspective).  
- Améliorations possibles :
  - historique détaillé des mensurations,
  - ajout de nouvelles mesures (cuisses, mollets, etc.),
  - calibration avancée avec objet de référence,
  - interface multilingue.
