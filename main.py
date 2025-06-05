from flask import Flask, render_template, request, url_for, redirect, session, flash, jsonify
import pymongo
from bson.objectid import ObjectId
import os
import bcrypt
import stripe
from functools import wraps
from jinja2 import TemplateNotFound

# =============== CONFIGURATION ===============

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuration de Stripe
stripe.api_key = "TA_CLE_STRIPE_SECRET"

# Connexion à MongoDB
try:
    mongo = pymongo.MongoClient("mongodb+srv://maru:marulegoat@cluster0.cqho6.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    mongo.server_info()  # Vérifie la connexion
    print("Connexion MongoDB réussie")
except pymongo.errors.ServerSelectionTimeoutError as err:
    print("Erreur MongoDB:", err)

# Accès aux collections
db_boutique = mongo["boutique"]
db_utilisateurs = db_boutique["utilisateurs"]
db_produits = db_boutique["produits"]
db_annonces = mongo["annonces"]["annonce"]

# =============== MIDDLEWARE POUR GÉRER LES RÔLES ===============

def role_required(role):
    """ Décorateur pour restreindre l'accès aux routes selon le rôle. """
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'util' not in session:
                flash("Vous devez être connecté pour accéder à cette page.", "danger")
                return redirect(url_for('login'))
            
            utilisateur = db_utilisateurs.find_one({'nom': session['util']})
            if not utilisateur or utilisateur.get('role') != role:
                flash("Accès refusé : Vous n'avez pas les permissions nécessaires.", "danger")
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return wrapper

# =============== INITIALISATION DE LA SESSION ===============

@app.before_request
def initialize_session():
    if 'rp' not in session:
        session['rp'] = 1_000_000  # 1M RP
    if 'be' not in session:
        session['be'] = 500_000  # 500K Blue Essence

# =============== ROUTES PRINCIPALES ===============

@app.route('/')
def index():
    try:
        annonces = list(db_annonces.find({}))
        return render_template('index.html', annonces=annonces)
    except Exception as e:
        print("Erreur annonces:", e)
        return render_template('index.html', annonces=[])

@app.route('/dashboard')
def dashboard():
    if 'util' not in session:
        return redirect(url_for('login'))
    
    utilisateur = db_utilisateurs.find_one({'nom': session['util']})

    if not utilisateur:
        return redirect(url_for('logout'))

    return render_template('dashboard.html', 
                           points=utilisateur.get('points', 0), 
                           rp=utilisateur.get('rp', 1_000_000), 
                           blue_essence=utilisateur.get('blue_essence', 1_000_000))

@app.route('/get_currency')
def get_currency():
    return jsonify({"rp": session.get('rp', 1_000_000), "be": session.get('be', 500_000)})

# =============== AUTHENTIFICATION ===============

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        if db_utilisateurs.find_one({'nom': request.form['utilisateur']}):
            return render_template('register.html', erreur="Ce pseudo existe déjà")
        
        if request.form['motdepasse'] == request.form['confirmation']:
            mdp_encrypte = bcrypt.hashpw(request.form['motdepasse'].encode('utf-8'), bcrypt.gensalt())
            db_utilisateurs.insert_one({
                'nom': request.form['utilisateur'],
                'mdp': mdp_encrypte,
                'points': 0,
                'rp': 1_000_000, 
                'blue_essence': 1_000_000,
                'role': 'utilisateur'  # Par défaut, l'utilisateur normal n'est pas admin
            })
            session['util'] = request.form['utilisateur']
            return redirect(url_for('dashboard'))
        else:
            return render_template('register.html', erreur="Les mots de passe doivent être identiques")
    return render_template('register.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        utilisateur = db_utilisateurs.find_one({'nom': request.form['utilisateur']})

        if utilisateur and bcrypt.checkpw(request.form['motdepasse'].encode('utf-8'), utilisateur['mdp']):
            session['util'] = request.form['utilisateur']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', erreur="Nom d'utilisateur ou mot de passe incorrect")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('util', None)
    return redirect(url_for('index'))

# =============== SYSTÈME DE BOUTIQUE ===============

@app.route('/boutique')
def boutique():
    if 'util' not in session:
        return redirect(url_for('login'))

    utilisateur = db_utilisateurs.find_one({'nom': session['util']})
    produits = list(db_produits.find())
    categories = {}

    for produit in produits:
        categorie = produit.get('categorie', 'Autre')
        if categorie not in categories:
            categories[categorie] = []
        categories[categorie].append(produit)

    return render_template('boutique.html', categories=categories, 
                           rp=utilisateur['rp'], 
                           blue_essence=utilisateur['blue_essence'])

@app.route('/acheter/<produit_id>', methods=['POST'])
def acheter_produit(produit_id):
    if 'util' not in session:
        return redirect(url_for('login'))

    produit = db_produits.find_one({"_id": ObjectId(produit_id)})
    utilisateur = db_utilisateurs.find_one({'nom': session['util']})

    if not produit or not utilisateur:
        return redirect(url_for('boutique'))

    if utilisateur['rp'] >= produit['prix']:
        db_utilisateurs.update_one({'nom': session['util']}, {'$inc': {'rp': -produit['prix']}})
        flash("Achat réussi avec RP !", "success")
    elif utilisateur['blue_essence'] >= produit['prix']:
        db_utilisateurs.update_one({'nom': session['util']}, {'$inc': {'blue_essence': -produit['prix']}})
        flash("Achat réussi avec Blue Essence !", "success")
    else:
        return render_template('erreur_achat.html', message="Vous n'avez pas assez de ressources.")

    return redirect(url_for('boutique'))

@app.route('/produit_detail/<produit_id>')
def produit_detail(produit_id):
    try:
        produit = db_produits.find_one({"_id": ObjectId(produit_id)})
        return render_template('produit_detail.html', produit=produit)
    except Exception as e:
        print(f"Erreur produit_detail: {e}")
        return render_template('produit_detail.html', produit=None)



# Optionnel: route explicite vers la page d'erreur 404 (pas obligatoire)
@app.route('/erreur-404')
def error_404():
    return render_template('erreur_404.html'), 404


# Gestion personnalisée de l'erreur 404 (page non trouvée)
@app.errorhandler(404)
def page_not_found(error):
    # On peut aussi logger l'erreur e si besoin
    return render_template('erreur_404.html'), 404





# =============== LANCEMENT DE L'APPLICATION ===============

if __name__ == '__main__':
    app.run(debug=True)
