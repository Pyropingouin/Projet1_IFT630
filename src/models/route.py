"""
Module: route.py
---------------
Définition des routes du réseau STS.

Gère les itinéraires entre les stations et intersections,
définissant les chemins que les bus peuvent emprunter.

Classes:
    Route: Définition d'un itinéraire

Dépendances:
    - models.intersection
    - models.station
    - models.stop

Relations:
    - Relie des Station et Intersection
    - Contient des Stop
    - Est utilisée par des Line

Attributs:
    id: Identifiant unique de la route
    stop_list: Liste ordonnée des arrêts
    origin_start: Point de départ (Station ou Intersection)
    origin_end: Point d'arrivée (Station ou Intersection)
    distance: Distance totale de la route
    direction: Direction de la route

Auteur: Hubert Ngankam
Email: hubert.ngankam@usherbrooke.ca
Session: H2025
Cours: IFT630
Version: 1.0
"""

from models.intersection import Intersection
from models.station import Station
from src.models.origin import Origin

# Route class representing a route in the system
class Route:
    def __init__(self, route_id, stop_list, origin_start, origin_end):
        """
        :param route_id: Identifiant unique pour la route
        :param stop_list: Liste des arrêts sur la route
        :param origin_start: L'origine de départ (Station ou Intersection)
        :param origin_end: L'origine d'arrivée (Station ou Intersection)
        """
        self.id = route_id
        self.stop_list = stop_list
        self.origin_start = origin_start
        self.origin_end = origin_end
        self.distance = self._calculate_distance()
        self.is_active = True
        self.direction = self._determine_direction()
        
    def __str__(self):
        stops_str = ', '.join(stop.name for stop in self.stop_list)
        return (f"Route ID: {self.id}, "
                f"De: {self.origin_start.name}, "
                f"À: {self.origin_end.name}, "
                f"Nombre d'arrêts: {len(self.stop_list)}, "
                f"Distance: {self.distance}, "
                f"Direction: {self.direction}, "
                f"Arrêts: [{stops_str}]")

    def _calculate_distance(self):
        """Calcule la distance totale de la route (en nombre d'arrêts)"""
        return len(self.stop_list)

    def _determine_direction(self):
        """Détermine la direction de la route basée sur les origines"""
        return f"{self.origin_start.name} → {self.origin_end.name}"

    def is_valid(self):
        """Vérifie si la route est valide"""
        # Vérifier qu'il y a au moins deux arrêts
        if len(self.stop_list) < 2:
            return False
            
        # Vérifier que les arrêts sont connectés
        for i in range(len(self.stop_list) - 1):
            if self.stop_list[i+1] not in self.stop_list[i].neighboring_stops:
                return False
                
        # Vérifier la connexion avec les origines
        if self.origin_start and self.origin_end:
            first_stop = self.stop_list[0]
            last_stop = self.stop_list[-1]
            
            # Vérifier si le premier arrêt est connecté à l'origine de départ
            if isinstance(self.origin_start, Station):
                if first_stop not in self.origin_start.stop_list:
                    return False
            elif isinstance(self.origin_start, Intersection):
                if first_stop not in self.origin_start.stop_list:
                    return False
                    
            # Vérifier si le dernier arrêt est connecté à l'origine d'arrivée
            if isinstance(self.origin_end, Station):
                if last_stop not in self.origin_end.stop_list:
                    return False
            elif isinstance(self.origin_end, Intersection):
                if last_stop not in self.origin_end.stop_list:
                    return False
                    
        return True

    def add_stop(self, stop, position=None):
        """
        Ajoute un arrêt à la route
        :param stop: L'arrêt à ajouter
        :param position: Position où insérer l'arrêt (optionnel)
        :return: True si l'ajout est réussi, False sinon
        """
        if position is None:
            # Ajouter à la fin
            if not self.stop_list or stop in self.stop_list[-1].neighboring_stops:
                self.stop_list.append(stop)
                self.distance = self._calculate_distance()
                return True
        else:
            # Ajouter à une position spécifique
            if 0 <= position <= len(self.stop_list):
                # Vérifier les connexions avec les arrêts voisins
                if position > 0 and stop not in self.stop_list[position-1].neighboring_stops:
                    return False
                if position < len(self.stop_list) and stop not in self.stop_list[position].neighboring_stops:
                    return False
                    
                self.stop_list.insert(position, stop)
                self.distance = self._calculate_distance()
                return True
        return False

    def remove_stop(self, stop):
        """
        Retire un arrêt de la route
        :return: True si le retrait est réussi, False sinon
        """
        if stop in self.stop_list:
            position = self.stop_list.index(stop)
            # Ne pas permettre le retrait du premier ou du dernier arrêt
            if position == 0 or position == len(self.stop_list) - 1:
                return False
                
            # Vérifier que les arrêts adjacents sont connectés
            prev_stop = self.stop_list[position - 1]
            next_stop = self.stop_list[position + 1]
            if next_stop not in prev_stop.neighboring_stops:
                return False
                
            self.stop_list.remove(stop)
            self.distance = self._calculate_distance()
            return True
        return False

    def get_next_stop(self, current_stop):
        """
        Retourne le prochain arrêt sur la route
        :param current_stop: L'arrêt actuel
        :return: Le prochain arrêt ou None
        """
        try:
            current_index = self.stop_list.index(current_stop)
            if current_index < len(self.stop_list) - 1:
                return self.stop_list[current_index + 1]
        except ValueError:
            pass
        return None

    def get_previous_stop(self, current_stop):
        """
        Retourne l'arrêt précédent sur la route
        :param current_stop: L'arrêt actuel
        :return: L'arrêt précédent ou None
        """
        try:
            current_index = self.stop_list.index(current_stop)
            if current_index > 0:
                return self.stop_list[current_index - 1]
        except ValueError:
            pass
        return None

    def get_remaining_stops(self, current_stop):
        """
        Retourne la liste des arrêts restants jusqu'à la fin de la route
        :param current_stop: L'arrêt actuel
        :return: Liste des arrêts restants
        """
        try:
            current_index = self.stop_list.index(current_stop)
            return self.stop_list[current_index + 1:]
        except ValueError:
            return []

    def contains_stop(self, stop):
        """Vérifie si un arrêt est sur cette route"""
        return stop in self.stop_list

    def get_stop_position(self, stop):
        """
        Retourne la position d'un arrêt sur la route
        :return: Index de l'arrêt ou -1 si non trouvé
        """
        try:
            return self.stop_list.index(stop)
        except ValueError:
            return -1

    def get_stops_between(self, start_stop, end_stop):
        """
        Retourne la liste des arrêts entre deux arrêts donnés
        :return: Liste des arrêts ou None si les arrêts ne sont pas sur la route
        """
        try:
            start_index = self.stop_list.index(start_stop)
            end_index = self.stop_list.index(end_stop)
            if start_index < end_index:
                return self.stop_list[start_index + 1:end_index]
            else:
                return self.stop_list[end_index + 1:start_index][::-1]
        except ValueError:
            return None

    def create_reverse_route(self, new_route_id):
        """
        Crée une nouvelle route dans la direction opposée
        :return: Nouvelle instance de Route
        """
        reversed_stops = self.stop_list[::-1]
        return Route(new_route_id, reversed_stops, self.origin_end, self.origin_start)
