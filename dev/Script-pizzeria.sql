CREATE DATABASE IF NOT EXISTS pizzeria;
USE pizzeria;

CREATE TABLE Clients (
    client_id INT PRIMARY KEY AUTO_INCREMENT,
    nom VARCHAR(100) NOT NULL,
    telephone VARCHAR(15),
    adresse TEXT
);

CREATE TABLE Commandes (
    commande_id INT PRIMARY KEY AUTO_INCREMENT,
    client_id INT,
    date_commande DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('en cours', 'livrée', 'annulée') DEFAULT 'en cours',
    FOREIGN KEY (client_id) REFERENCES Clients(client_id) ON DELETE CASCADE
);
CREATE TABLE livrer_commande (
    livraison_id INT AUTO_INCREMENT PRIMARY KEY,
    commande_id INT,
    date_livraison DATETIME DEFAULT CURRENT_TIMESTAMP,
    livre_par VARCHAR(100),
    FOREIGN KEY (commande_id) REFERENCES Commandes(commande_id)
);

CREATE TABLE Croutes (
    croute_id INT PRIMARY KEY AUTO_INCREMENT,
    type_croute VARCHAR(50) NOT NULL
);

CREATE TABLE Sauces (
    sauce_id INT PRIMARY KEY AUTO_INCREMENT,
    type_sauce VARCHAR(50) NOT NULL
);

CREATE TABLE Garnitures (
    garniture_id INT PRIMARY KEY AUTO_INCREMENT,
    type_garniture VARCHAR(50) NOT NULL
);

CREATE TABLE Pizzas (
    pizza_id INT PRIMARY KEY AUTO_INCREMENT,
    commande_id INT,
    croute_id INT,
    sauce_id INT,
    FOREIGN KEY (commande_id) REFERENCES Commandes(commande_id) ON DELETE CASCADE,
    FOREIGN KEY (croute_id) REFERENCES Croutes(croute_id),
    FOREIGN KEY (sauce_id) REFERENCES Sauces(sauce_id)
);

CREATE TABLE Pizza_Garniture (
    pizza_id INT,
    garniture_id INT,
    PRIMARY KEY (pizza_id, garniture_id),
    FOREIGN KEY (pizza_id) REFERENCES Pizzas(pizza_id) ON DELETE CASCADE,
    FOREIGN KEY (garniture_id) REFERENCES Garnitures(garniture_id)
);
CREATE TABLE listeattente (
    id INT PRIMARY KEY AUTO_INCREMENT,
    commande_id INT,
    client_id INT,
    date_commande DATETIME,
    status ENUM('en cours', 'livrée', 'annulée') DEFAULT 'en cours',
    FOREIGN KEY (commande_id) REFERENCES Commandes(commande_id) ON DELETE CASCADE
);

DELIMITER $$

CREATE TRIGGER After_Commande_Insert
AFTER INSERT ON Commandes
FOR EACH ROW
BEGIN
    -- Insertion automatique de la commande dans la table Liste_Attente
    IF NEW.status = 'en cours' THEN
        INSERT INTO listeattente (commande_id, client_id, date_commande, status)
        VALUES (NEW.commande_id, NEW.client_id, NEW.date_commande, 'en cours');
    END IF;
END$$

DELIMITER ;
 