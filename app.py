from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

import os
from werkzeug.utils import secure_filename
from math import sqrt
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

app = Flask(__name__)
app.secret_key = "change_ce_secret"

# ---------- Upload ----------
UPLOAD_FOLDER = os.path.join("static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------- Connexion à la BDD ----------
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="mesuria",
    )
    return conn


# ---------- Routes ----------

# Accueil
@app.route("/")
def home():
    return render_template("Accueil.html")


# Création de compte
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        email = request.form.get("email")
        password = request.form.get("password")
        password2 = request.form.get("password2")

        if not email or not password or not password2:
            return render_template(
                "compte.html",
                error="Merci de remplir tous les champs.",
            )
        if password != password2:
            return render_template(
                "compte.html",
                error="Les mots de passe ne correspondent pas.",
            )

        conn = get_db_connection()
        cur = conn.cursor()

        # vérifier si l'email existe déjà
        cur.execute("SELECT id_users FROM users WHERE email = %s", (email,))
        existing = cur.fetchone()
        if existing:
            cur.close()
            conn.close()
            return render_template(
                "compte.html",
                error="Un compte existe déjà avec cet e-mail.",
            )

        password_hash = generate_password_hash(password)

        cur.execute(
            """
            INSERT INTO users (Nom, Prenom, email, Mot_de_passe, Date_de_creation)
            VALUES (%s, %s, %s, %s, NOW())
            """,
            (nom, prenom, email, password_hash),
        )
        conn.commit()
        cur.close()
        conn.close()

        return render_template(
            "compte.html",
            message="Compte créé. Vous pouvez vous connecter.",
        )

    return render_template("compte.html")


# Connexion
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return render_template(
                "seconnecter.html",
                error="Merci de remplir tous les champs.",
            )

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        # récupérer l'utilisateur
        cur.execute(
            "SELECT id_users, Mot_de_passe FROM users WHERE email = %s",
            (email,),
        )
        user = cur.fetchone()
        cur.close()
        conn.close()

        # email inconnu ou mot de passe faux
        if not user or not check_password_hash(user["Mot_de_passe"], password):
            return render_template(
                "seconnecter.html",
                error="E-mail ou mot de passe incorrect.",
            )

        # connexion OK : on garde l'id en session
        session["user_id"] = user["id_users"]

        # redirection vers la page mensurations
        return redirect(url_for("mensurations"))

    return render_template("seconnecter.html")


# Page mensurations avec upload de photo
@app.route("/mensurations", methods=["GET", "POST"])
def mensurations():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        # -------- vérification du fichier --------
        if "photo" not in request.files:
            return render_template(
                "Mensurations.html",
                error="Aucun fichier reçu.",
            )

        file = request.files["photo"]

        if file.filename == "":
            return render_template(
                "Mensurations.html",
                error="Aucun fichier sélectionné.",
            )

        if not allowed_file(file.filename):
            return render_template(
                "Mensurations.html",
                error="Type de fichier non autorisé.",
            )

        # -------- sauvegarde --------
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(save_path)

        # -------- chargement modèle MediaPipe --------
        MODEL_PATH = "pose_landmarker_full.task"
        if not os.path.exists(MODEL_PATH):
            import urllib.request

            url = (
                "https://storage.googleapis.com/mediapipe-models/"
                "pose_landmarker/pose_landmarker_full/float16/1/"
                "pose_landmarker_full.task"
            )
            urllib.request.urlretrieve(url, MODEL_PATH)

        image_bgr = cv2.imread(save_path)
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)

        base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            output_segmentation_masks=False,
        )
        detector = vision.PoseLandmarker.create_from_options(options)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=image_rgb,
        )
        result = detector.detect(mp_image)

        h, w, _ = image_bgr.shape
        epaule_px = poitrine_px = torse_px = bras_px = taille_px = jambe_px = None

        # -------- calcul des mensurations --------
        if result.pose_landmarks:
            pose_landmarks = result.pose_landmarks[0]

            def lm_px(index):
                lm = pose_landmarks[index]
                return int(lm.x * w), int(lm.y * h)

            # Indices MediaPipe Pose
            LEFT_SHOULDER = 11
            RIGHT_SHOULDER = 12
            LEFT_ELBOW = 13
            LEFT_WRIST = 15
            LEFT_HIP = 23
            RIGHT_HIP = 24
            LEFT_KNEE = 25
            LEFT_ANKLE = 27

            # Épaules
            sx, sy = lm_px(LEFT_SHOULDER)
            dx, dy = lm_px(RIGHT_SHOULDER)
            epaule_px = sqrt((dx - sx) ** 2 + (dy - sy) ** 2)

            # Poitrine (largeur horizontale entre les épaules)
            poitrine_px = abs(dx - sx)

            # Hanches
            hx_left, hy_left = lm_px(LEFT_HIP)
            hx_right, hy_right = lm_px(RIGHT_HIP)

            # Torse : distance moyenne épaules ↔ hanches
            torse_px = sqrt(
                ((hx_left + hx_right) / 2 - (sx + dx) / 2) ** 2
                + ((hy_left + hy_right) / 2 - (sy + dy) / 2) ** 2
            )

            # Bras gauche : épaule → poignet
            wx, wy = lm_px(LEFT_WRIST)
            bras_px = sqrt((wx - sx) ** 2 + (wy - sy) ** 2)

            # Tour de taille : largeur entre hanches
            taille_px = abs(hx_right - hx_left)

            # Jambe gauche : hanche → cheville (hanche-genou + genou-cheville)
            kx, ky = lm_px(LEFT_KNEE)
            ax, ay = lm_px(LEFT_ANKLE)
            haut_jambe = sqrt((kx - hx_left) ** 2 + (ky - hy_left) ** 2)
            bas_jambe = sqrt((ax - kx) ** 2 + (ay - ky) ** 2)
            jambe_px = haut_jambe + bas_jambe

        # -------- enregistrement BDD (optionnel) --------
        user_id = session["user_id"]
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO mensurations (date_analyse, id_users)
            VALUES (NOW(), %s)
            """,
            (user_id,),
        )
        conn.commit()
        cur.close()
        conn.close()

        # -------- retour page HTML avec résultats --------
        return render_template(
            "Mensurations.html",
            message="Analyse terminée.",
            epaule=epaule_px,
            poitrine=poitrine_px,
            torse=torse_px,
            bras=bras_px,
            tour_taille=taille_px,
            jambe=jambe_px,
        )

    # GET simple
    return render_template("Mensurations.html")


# Déconnexion
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
