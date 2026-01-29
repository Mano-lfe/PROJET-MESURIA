from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "change_ce_secret"


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
        database="mesuria"
    )
    return conn


# ---------- Routes ----------

# Accueil
@app.route("/Accueil")
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
            return render_template("compte.html",
                                   error="Merci de remplir tous les champs.")
        if password != password2:
            return render_template("compte.html",
                                   error="Les mots de passe ne correspondent pas.")

        conn = get_db_connection()
        cur = conn.cursor()

        # vérifier si l'email existe déjà
        cur.execute("SELECT id_users FROM users WHERE email = %s", (email,))
        existing = cur.fetchone()
        if existing:
            cur.close()
            conn.close()
            return render_template("compte.html",
                                   error="Un compte existe déjà avec cet e-mail.")

        password_hash = generate_password_hash(password)

        cur.execute(
            "INSERT INTO users (Nom, Prenom, email, Mot_de_passe, Date_de_creation) VALUES (%s, %s, %s, %s, NOW())",
            (nom, prenom, email, password_hash)
        )
        conn.commit()
        cur.close()
        conn.close()

        return render_template("compte.html",
                               message="Compte créé. Vous pouvez vous connecter.")

    return render_template("compte.html")


# Connexion
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return render_template("seconnecter.html",
                                   error="Merci de remplir tous les champs.")

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        # récupérer l'utilisateur
        cur.execute("SELECT id_users, Mot_de_passe FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        # email inconnu ou mot de passe faux
        if not user or not check_password_hash(user["Mot_de_passe"], password):
            return render_template("seconnecter.html",
                                   error="E-mail ou mot de passe incorrect.")

        # connexion OK : on garde l'id en session
        session["user_id"] = user["id_users"]

        # redirection vers la page mensurations
        return redirect(url_for("mensurations"))

    return render_template("seconnecter.html")


# Page mensurations (ici juste protégée, sans upload pour l'instant)
@app.route("/mensurations")
def mensurations():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("Mensurations.html")


# Déconnexion
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)
