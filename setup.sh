#!/bin/bash

# 1. Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "Python3 n'est pas installé. Veuillez l'installer et réessayer. stp"
    exit 1
fi

# 2. Créer un environnement virtuel s'il n'existe pas déjà
if [ ! -d "venv" ]; then
    echo "Création de l'environnement virtuel..."
    python3 -m venv venv
else
    echo "L'environnement virtuel existe déjà."
fi

# 3. Activer l'environnement virtuel
echo "Activation de l'environnement virtuel..."
source venv/bin/activate

# 4. Installer les dépendances
if [ -f "requirements.txt" ]; then
    echo "Installation des dépendances à partir de requirements.txt..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "Fichier requirements.txt introuvable. Assurez-vous qu'il est présent dans le projet."
fi

# 5. Fin du script
echo "Initialisation terminée."
