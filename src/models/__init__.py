"""
Package: models
-------------
Modèles de données pour le réseau de transport STS.

Ce package contient toutes les classes représentant les éléments
du réseau de transport : bus, stations, arrêts, passagers, etc.

Contenu:
    - origin.py: Classe de base pour les éléments positionnables
    - bus.py: Gestion des véhicules
    - station.py: Stations principales
    - stop.py: Arrêts de bus
    - intersection.py: Points de connexion
    - line.py: Lignes de bus
    - route.py: Itinéraires
    - passenger.py: Gestion des passagers

Relations:
    Origin
    ├── Station
    ├── Stop
    └── Intersection

    Line
    ├── Route
    └── Bus

Auteur: Hubert Ngankam
Email: hubert.ngankam@usherbrooke.ca
Session: H2025
Cours: IFT630
Version: 1.0
"""

from .passenger import Passenger
from .bus import Bus
