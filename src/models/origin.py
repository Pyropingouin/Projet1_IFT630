"""
Module: origin.py
----------------
Classe de base pour les éléments du réseau STS ayant une position ou une origine.

Cette classe sert de base aux stations, arrêts et intersections. Elle fournit
les fonctionnalités communes de connexion et de gestion des origines.

Classes:
    Origin: Classe de base pour les éléments positionnables du réseau

Relations:
    - Classe parente de Station, Stop, et Intersection
    - Gère les connexions entre différentes origines
    - Maintient les listes de stops et routes associés

Attributs:
    origin_id: Identifiant unique de l'origine
    name: Nom de l'origine
    location_type: Type de localisation (station, stop, intersection)
    connected_origins: Liste des origines connectées
    stop_list: Liste des arrêts associés
    routes_starting: Routes qui commencent à cette origine
    routes_ending: Routes qui terminent à cette origine

Auteur: Hubert Ngankam
Email: hubert.ngankam@usherbrooke.ca
Session: H2025
Cours: IFT630
Version: 1.0
"""

class Origin:
    def __init__(self, origin_id, name, location_type=None):
        """
        :param origin_id: Unique ID for the origin
        :param name: Name of the origin
        :param location_type: Type of location (station, stop, intersection)
        """
        self.origin_id = origin_id
        self.name = name
        self.location_type = location_type
        self.connected_origins = []  # Liste des origines connectées
        self.stop_list = []  # Liste des arrêts associés à cette origine
        self.routes_starting = []  # Routes qui commencent à cette origine
        self.routes_ending = []    # Routes qui terminent à cette origine

    def __str__(self):
        """Représentation en chaîne de caractères de l'origine"""
        return (f"Origin ID: {self.origin_id}, "
                f"Name: {self.name}, "
                f"Type: {self.location_type}, "
                f"Stops: {len(self.stop_list)}, "
                f"Connected to: {len(self.connected_origins)}")

    def add_stop(self, stop):
        """Ajoute un arrêt à l'origine"""
        if stop not in self.stop_list:
            self.stop_list.append(stop)
            return True
        return False

    def remove_stop(self, stop):
        """Retire un arrêt de l'origine"""
        if stop in self.stop_list:
            self.stop_list.remove(stop)
            return True
        return False

    def connect_to(self, other_origin):
        """Connecte cette origine à une autre origine"""
        if other_origin not in self.connected_origins:
            self.connected_origins.append(other_origin)
            if self not in other_origin.connected_origins:
                other_origin.connected_origins.append(self)
            return True
        return False

    def disconnect_from(self, other_origin):
        """Déconnecte cette origine d'une autre origine"""
        if other_origin in self.connected_origins:
            self.connected_origins.remove(other_origin)
            if self in other_origin.connected_origins:
                other_origin.connected_origins.remove(self)
            return True
        return False

    def add_route(self, route, is_starting=True):
        """Ajoute une route partant de ou arrivant à cette origine"""
        if is_starting:
            if route not in self.routes_starting:
                self.routes_starting.append(route)
                return True
        else:
            if route not in self.routes_ending:
                self.routes_ending.append(route)
                return True
        return False

    def remove_route(self, route, is_starting=True):
        """Retire une route de cette origine"""
        if is_starting:
            if route in self.routes_starting:
                self.routes_starting.remove(route)
                return True
        else:
            if route in self.routes_ending:
                self.routes_ending.remove(route)
                return True
        return False

    def get_all_routes(self):
        """Retourne toutes les routes associées à cette origine"""
        return self.routes_starting + self.routes_ending

    def get_connected_stops(self):
        """Retourne tous les arrêts connectés (directs et via origines connectées)"""
        all_stops = set(self.stop_list)
        for origin in self.connected_origins:
            all_stops.update(origin.stop_list)
        return list(all_stops)

    def is_connected_to(self, other_origin):
        """Vérifie si cette origine est connectée à une autre origine"""
        return other_origin in self.connected_origins

    def is_stop_accessible(self, stop):
        """Vérifie si un arrêt est accessible depuis cette origine"""
        if stop in self.stop_list:
            return True
        for origin in self.connected_origins:
            if stop in origin.stop_list:
                return True
        return False

    def get_connection_path_to(self, target_origin, visited=None):
        """
        Trouve un chemin de connexion vers une origine cible
        Retourne la liste des origines formant le chemin
        """
        if visited is None:
            visited = set()
            
        if self == target_origin:
            return [self]
            
        visited.add(self)
        
        for origin in self.connected_origins:
            if origin not in visited:
                path = origin.get_connection_path_to(target_origin, visited)
                if path:
                    return [self] + path
                    
        return None