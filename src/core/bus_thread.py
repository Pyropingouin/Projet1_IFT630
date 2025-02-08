"""
Module: component_threads.py
--------------------------
Implémentation des threads pour chaque composant du réseau STS.

Définit le comportement spécifique des threads pour les bus,
stations, arrêts, passagers et intersections.

Classes:
    BusThread: Thread de simulation pour un bus
    StationThread: Thread de simulation pour une station
    StopThread: Thread de simulation pour un arrêt
    PassengerThread: Thread de simulation pour un passager
    IntersectionThread: Thread de simulation pour une intersection

Auteur: Hubert Ngankam
Email: hubert.ngankam@usherbrooke.ca
Session: H2025
Cours: IFT630
Version: 1.0
"""
from threading import Thread
from src.core.base_component_thread import BaseComponentThread


class BusThread(BaseComponentThread):
    def __init__(self, bus, stop_event):
        super().__init__(bus, stop_event, f"Bus-{bus.name}")
        self._verify_and_fix_bus_initialization()
        
    def _verify_and_fix_bus_initialization(self):
        """Vérifie et corrige l'initialisation du bus"""
        try:
            if not self.component.current_route:
                self.logger.warning(f"Bus {self.component.id}: Pas de route assignée")
                return False

            if not self.component.current_stop:
                self.logger.warning(f"Bus {self.component.id}: Pas d'arrêt actuel")
                # Assigner le premier arrêt de la route
                if self.component.current_route.stop_list:
                    self.component.current_stop = self.component.current_route.stop_list[0]
                    self.logger.info(
                        f"Bus {self.component.id}: Assigné à l'arrêt initial {self.component.current_stop.name}"
                    )
                return True

            # Vérifier si l'arrêt actuel est dans la route
            if self.component.current_stop not in self.component.current_route.stop_list:
                self.logger.warning(
                    f"Bus {self.component.id}: Arrêt actuel {self.component.current_stop.name} "
                    f"non trouvé dans la route - réinitialisation"
                )
                # Réinitialiser à l'arrêt initial de la route
                self.component.current_stop = self.component.current_route.stop_list[0]
                self.logger.info(
                    f"Bus {self.component.id}: Réinitialisé à l'arrêt {self.component.current_stop.name}"
                )

            return True

        except Exception as e:
            self.logger.error(f"Bus {self.component.id}: Erreur d'initialisation - {str(e)}")
            return False
    
    def run(self):
        """Boucle principale du thread"""
        if not self._verify_and_fix_bus_initialization():
            self.logger.error(f"Bus {self.component.id}: Impossible de démarrer - initialisation incorrecte")
            return

        while not self.stop_event.is_set():
            try:
                if not self.component.current_route:
                    self.logger.error(f"Bus {self.component.id}: Pas de route assignée")
                    break

                if not self.component.current_stop:
                    self.logger.error(f"Bus {self.component.id}: Pas d'arrêt actuel")
                    break

                # Log de l'état actuel
                self.logger.info(
                    f"🚌 Bus {self.component.id} à {self.component.current_stop.name} - "
                    f"Passagers: {len(self.component.passenger_list)}/{self.component.capacity} - "
                    f"Route: {self.component.current_route.id}"
                )

                # Gérer les passagers à l'arrêt actuel
                self._handle_passenger_exchange()
                self.sleep_random(2, 4)

                # Tenter de se déplacer vers le prochain arrêt
                if not self._move_to_next_stop():
                    self.logger.warning(
                        f"Bus {self.component.id}: Impossible de se déplacer depuis "
                        f"{self.component.current_stop.name}"
                    )
                else:
                    self.logger.info(
                        f"➡️ Bus {self.component.id} en route vers {self.component.current_stop.name}"
                    )
                self.sleep_random(3, 5)

            except Exception as e:
                self.logger.error(f"Bus {self.component.id}: Erreur - {str(e)}")
                self.sleep_random(2, 4)

    def _move_to_next_stop(self):
        """Déplace le bus vers le prochain arrêt avec vérifications de sécurité"""
        try:
            if not self.component.current_route or not self.component.current_stop:
                self.logger.error(f"Bus {self.component.id} n'a pas de route")
                return False

            route_stops = self.component.current_route.stop_list
            if not route_stops:
                self.logger.error(f"Bus {self.component.id}: Route sans arrêts")
                return False

            # Trouver l'index de l'arrêt actuel
            try:
                current_index = route_stops.index(self.component.current_stop)
            except ValueError:
                self.logger.error(
                    f"Bus {self.component.id}: Arrêt actuel {self.component.current_stop.name} "
                    f"non trouvé dans la route"
                )
                # Réinitialiser au premier arrêt
                self.component.current_stop = route_stops[0]
                return True

            # Déterminer le prochain arrêt
            if current_index < len(route_stops) - 1:
                next_stop = route_stops[current_index + 1]
            else:
                # Fin de la route, retour au début
                next_stop = route_stops[0]
                self.logger.info(f"Bus {self.component.id}: Retour au début de la route")

            # Notification des arrêts
            if hasattr(self.component.current_stop, 'bus_departure'):
                self.component.current_stop.bus_departure(self.component)

            # Déplacement
            old_stop = self.component.current_stop
            self.component.current_stop = next_stop

            if hasattr(next_stop, 'bus_arrival'):
                next_stop.bus_arrival(self.component)

            self.logger.info(
                f"Bus {self.component.id}: Déplacement de {old_stop.name} vers {next_stop.name}"
            )
            return True

        except Exception as e:
            self.logger.error(
                f"Bus {self.component.id}: Erreur lors du déplacement - {str(e)}"
            )
            return False
    def _handle_passenger_exchange(self):
        """Gère l'échange de passagers à l'arrêt"""
        if not self.component.current_stop:
            return

        # Débarquement
        self._handle_alighting()
        
        # Embarquement
        self._handle_boarding()

    def _handle_alighting(self):
        """Gère le débarquement des passagers"""
        alighting_passengers = [p for p in self.component.passenger_list 
                              if self._should_passenger_alight(p)]
        
        for passenger in alighting_passengers:
            if self.component.remove_passenger(passenger):
                self.logger.info(
                    f"⬇️ Passager {passenger.name} descend du bus {self.component.id} "
                    f"à {self.component.current_stop.name}"
                )

    def _should_passenger_alight(self, passenger) -> bool:
        """Vérifie si un passager doit descendre à l'arrêt actuel"""
        current_stop = self.component.current_stop
        
        # Vérification directe de la destination
        if passenger.destination == current_stop:
            return True
            
        # Si la destination est une station, vérifier si l'arrêt en fait partie
        if hasattr(passenger.destination, 'stop_list'):
            return current_stop in passenger.destination.stop_list
            
        return False

    def _handle_boarding(self):
        """Gère l'embarquement des passagers"""
        if self.component.is_full():
            return

        waiting_passengers = self.component.current_stop.waiting_passengers.copy()
        for passenger in waiting_passengers:
            if (self.component.can_accept_passengers() and 
                self._can_accept_passenger(passenger)):
                if self.component.add_passenger(passenger):
                    self.component.current_stop.remove_passenger(passenger)
                    self.logger.info(
                        f"⬆️ Passager {passenger.name} monte dans le bus {self.component.id} "
                        f"à {self.component.current_stop.name}"
                    )

    def _can_accept_passenger(self, passenger) -> bool:
        """Vérifie si le bus peut accepter ce passager"""
        if not self.component.current_route:
            return False
            
        route_stops = self.component.current_route.stop_list
        current_index = route_stops.index(self.component.current_stop)
        
        # Si la destination est une station, vérifier si un de ses arrêts est sur notre route
        if hasattr(passenger.destination, 'stop_list'):
            for stop in passenger.destination.stop_list:
                if stop in route_stops[current_index:]:
                    return True
        # Si la destination est un arrêt, vérifier s'il est sur notre route
        elif passenger.destination in route_stops[current_index:]:
            return True
            
        return False
 