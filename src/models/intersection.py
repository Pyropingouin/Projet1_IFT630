"""
Module: intersection.py
----------------------
Implémentation des intersections du réseau STS.

Gère les points de connexion entre différentes routes et permet
les transferts entre lignes de bus.

Classes:
    Intersection: Point de connexion du réseau

Dépendances:
    - models.origin
    - models.station
    - models.stop

Relations:
    - Hérite de Origin
    - Connecte plusieurs Station et Stop
    - Point de passage pour les Route

Attributs:
    intersection_id: Identifiant unique de l'intersection
    stop_list: Liste des arrêts à l'intersection
    neighbors: Liste des intersections voisines

Auteur: Hubert Ngankam
Email: hubert.ngankam@usherbrooke.ca
Session: H2025
Cours: IFT630
Version: 1.0
"""

from models.station import Station
from models.stop import Stop
from src.models.origin import Origin

class Intersection(Origin):
    def __init__(self, origin_id, name, intersection_id, stop_list=None, neighbors=None):
        """
        :param origin_id: Identifiant de l'origine
        :param name: Nom de l'intersection
        :param intersection_id: Identifiant unique de l'intersection
        :param stop_list: Liste des arrêts de l'intersection
        :param neighbors: Liste des intersections voisines
        """
        super().__init__(origin_id, name, location_type="intersection")
        self.intersection_id = intersection_id
        self.stop_list = stop_list if stop_list is not None else []
        
        # Connexion avec les intersections voisines
        if neighbors:
            for neighbor in neighbors:
                self.connect_to(neighbor)

    def __str__(self):
        connected_intersections = [origin.name for origin in self.connected_origins 
                                 if origin.location_type == "intersection"]
        return (f"Intersection ID: {self.intersection_id}, Name: {self.name}, "
                f"Stops: {len(self.stop_list)}, "
                f"Connected Intersections: {connected_intersections}")

    def add_neighbor(self, neighbor):
        """Ajoute une intersection voisine"""
        if neighbor.location_type == "intersection":
            return self.connect_to(neighbor)
        return False

    def remove_neighbor(self, neighbor):
        """Retire une intersection voisine"""
        if neighbor.location_type == "intersection":
            return self.disconnect_from(neighbor)
        return False

    def get_neighbor_intersections(self):
        """Retourne toutes les intersections voisines"""
        return [origin for origin in self.connected_origins 
                if origin.location_type == "intersection"]

    def get_connected_stations(self):
        """Retourne toutes les stations connectées"""
        return [origin for origin in self.connected_origins 
                if origin.location_type == "station"]

    def can_reach_destination(self, destination):
        """Vérifie si une destination peut être atteinte depuis cette intersection"""
        if isinstance(destination, Stop):
            return destination in self.get_all_stops()
        elif isinstance(destination, Station):
            return destination in self.get_connected_stations()
        elif isinstance(destination, Intersection):
            return self.get_connection_path_to(destination) is not None
        return False

    def add_stop(self, stop):
        """Ajoute un stop à l'intersection"""
        if stop not in self.stop_list:
            self.stop_list.append(stop)
            stop.intersection = self  # Référence à l'intersection dans le stop
