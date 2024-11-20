from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev")  # Utilise "dev" comme valeur par défaut pour le développement

# Connexion à la base de données MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mysql",
    database="pizzeria"
)

@app.route('/')
def index():
    return redirect(url_for('commande'))

# Route pour la page de formulaire de commande
@app.route('/commande', methods=['GET', 'POST'])
def commande():
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.form['nom']
        telephone = request.form['telephone']
        adresse = request.form['adresse']
        croute = request.form['croute']
        sauce = request.form['sauce']
        garnitures = request.form.getlist('garniture')

        # Sauvegarder les informations dans la session pour l'affichage du résumé
        session['commande'] = {
            'nom': nom,
            'telephone': telephone,
            'adresse': adresse,
            'type_croute': croute,
            'type_sauce': sauce,
            'garnitures': garnitures
        }
        
        # Rediriger vers la page de résumé
        return redirect(url_for('resumer_commande'))
    
    return render_template('commande.html')

# Route pour afficher le résumé de la commande
@app.route('/resumer_commande', methods=['GET', 'POST'])
def resumer_commande():
    # Récupérer les informations de la commande depuis la session
    commande = session.get('commande', None)
    
    if not commande:
        return redirect(url_for('commande'))  # Redirige vers le formulaire si pas de données

    if request.method == 'POST':
        # Insérer les informations de la commande dans la base de données
        cursor = db.cursor()
        
        # Insérer les informations du client
        cursor.execute("INSERT INTO Clients (nom, telephone, adresse) VALUES (%s, %s, %s)", 
                       (commande['nom'], commande['telephone'], commande['adresse']))
        client_id = cursor.lastrowid  # Obtenir l'ID du client nouvellement inséré

        # Insérer la commande dans la table Commandes
        cursor.execute("INSERT INTO Commandes (client_id, status) VALUES (%s, 'en cours')", (client_id,))
        commande_id = cursor.lastrowid  # Obtenir l'ID de la commande nouvellement insérée

        # Insérer la pizza dans la table Pizzas
        cursor.execute("INSERT INTO Pizzas (commande_id, croute_id, sauce_id) VALUES (%s, %s, %s)",
                       (commande_id, commande['type_croute'], commande['type_sauce']))
        pizza_id = cursor.lastrowid  # Obtenir l'ID de la pizza

        # Insérer les garnitures dans la table Pizza_Garniture
        for garniture in commande['garnitures']:
            cursor.execute("INSERT INTO Pizza_Garniture (pizza_id, garniture_id) VALUES (%s, %s)", (pizza_id, garniture))

        db.commit()  # Enregistrer les modifications
        cursor.close()

        # Effacer la commande de la session après confirmation
        session.pop('commande', None)

        # Rediriger vers une page de succès ou de confirmation
        return redirect(url_for('commandes_en_attente'))

    return render_template('resumer_commande.html', commande=commande)

# Route pour afficher les commandes en attente
@app.route('/commandes_en_attente')
def commandes_en_attente():
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            Commandes.commande_id,
            Clients.nom,
            Clients.telephone,
            Clients.adresse,
            Commandes.date_commande,
            MAX(Croutes.type_croute) AS type_croute,  -- Utiliser MAX pour éviter le problème avec ONLY_FULL_GROUP_BY
            MAX(Sauces.type_sauce) AS type_sauce,      -- Utiliser MAX ici aussi
            GROUP_CONCAT(Garnitures.type_garniture SEPARATOR ', ') AS garnitures
        FROM Commandes
        JOIN Clients ON Commandes.client_id = Clients.client_id
        JOIN Pizzas ON Commandes.commande_id = Pizzas.commande_id
        JOIN Croutes ON Pizzas.croute_id = Croutes.croute_id
        JOIN Sauces ON Pizzas.sauce_id = Sauces.sauce_id
        JOIN Pizza_Garniture ON Pizzas.pizza_id = Pizza_Garniture.pizza_id
        JOIN Garnitures ON Pizza_Garniture.garniture_id = Garnitures.garniture_id
        WHERE Commandes.status = 'en cours'
        GROUP BY Commandes.commande_id
    """)
    commandes = cursor.fetchall()
    cursor.close()
    return render_template('commandes_en_attente.html', commandes=commandes)

# Route pour marquer une commande comme livrée
@app.route('/livrer_commande/<int:commande_id>', methods=['POST'])
def livrer_commande(commande_id):
    cursor = db.cursor()
    cursor.execute("UPDATE Commandes SET status = 'livrée' WHERE commande_id = %s", (commande_id,))
    db.commit()
    cursor.close()
    return redirect(url_for('commandes_en_attente'))

if __name__ == '__main__':
    app.run(debug=True)
