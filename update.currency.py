# update_currency.py
import pymongo

# Connexion à MongoDB
mongo = pymongo.MongoClient("mongodb+srv://maru:marulegoat@cluster0.cqho6.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db_boutique = mongo["boutique"]
db_utilisateurs = db_boutique["utilisateurs"]

def update_rp_and_be(username, rp_spent, be_spent):
    """
    Fonction qui met à jour les points RP et Blue Essence d'un utilisateur après un achat.
    
    :param username: Le nom d'utilisateur de l'utilisateur
    :param rp_spent: Les points RP dépensés
    :param be_spent: Les points Blue Essence dépensés
    """
    try:
        utilisateur = db_utilisateurs.find_one({'nom': username})
        
        if utilisateur:
            # Si l'utilisateur a suffisamment de RP ou BE, les ressources sont mises à jour
            if utilisateur['rp'] >= rp_spent:
                db_utilisateurs.update_one({'nom': username}, {'$inc': {'rp': -rp_spent}})
            elif utilisateur['blue_essence'] >= be_spent:
                db_utilisateurs.update_one({'nom': username}, {'$inc': {'blue_essence': -be_spent}})
            else:
                print(f"{username} n'a pas assez de ressources.")
                return False  # Si l'utilisateur n'a pas assez de ressources
            return True
        else:
            print(f"L'utilisateur {username} n'existe pas.")
            return False
    except Exception as e:
        print(f"Erreur lors de la mise à jour des ressources pour {username}: {e}")
        return False
" "