"""
Module: station.py
-----------------
Implémentation des stations du réseau STS.

Gère les stations principales du réseau, leurs arrêts
et leurs connexions avec les intersections.

Classes:
    Station: Station principale du réseau

Dépendances:
    - models.origin
    - models.stop
    - models.intersection

Relations:
    - Hérite de Origin
    - Contient des Stop
    - Connectée à des Intersection

Attributs:
    station_id: Identifiant unique de la station
    stop_list: Liste des arrêts de la station
    intersection_list: Liste des intersections connectées

Auteur: Hubert Ngankam
Email: hubert.ngankam@usherbrooke.ca
Session: H2025
Cours: IFT630
Version: 1.0
"""

from src.models.origin import Origin

# Station class representing a station in the system
class Station(Origin):
    def __init__(self, origin_id, station_id, name, stop_list=None, intersection_list=None):
        """
        :param origin_id: Identifiant de l'origine
        :param station_id: Identifiant unique de la station
        :param name: Nom de la station
        :param stop_list: Liste des arrêts de la station
        :param intersection_list: Liste des intersections connectées
        """
        super().__init__(origin_id, name, location_type="station")
        self.station_id = station_id
        self.stop_list = stop_list if stop_list is not None else []
        
        # Connexion automatique avec les intersections
        if intersection_list:
            for intersection in intersection_list:
                self.connect_to(intersection)
                
    def __str__(self):
        connected_intersections = [origin.name for origin in self.connected_origins 
                                 if origin.location_type == "intersection"]
        return (f"Station ID: {self.station_id}, Name: {self.name}, "
                f"Stops: {len(self.stop_list)}, "
                f"Connected Intersections: {connected_intersections}")

    def add_intersection(self, intersection):
        """Ajoute une intersection à la station"""
        if intersection.location_type == "intersection":
            return self.connect_to(intersection)
        return False

    def remove_intersection(self, intersection):
        """Retire une intersection de la station"""
        if intersection.location_type == "intersection":
            return self.disconnect_from(intersection)
        return False

    def get_accessible_stops(self):
        """Retourne tous les arrêts accessibles depuis cette station"""
        accessible_stops = set(self.stop_list)
        for intersection in self.get_connected_intersections():
            accessible_stops.update(intersection.stop_list)
        return list(accessible_stops)

    def get_connected_intersections(self):
        """Retourne toutes les intersections connectées"""
        return [origin for origin in self.connected_origins 
                if origin.location_type == "intersection"]
        