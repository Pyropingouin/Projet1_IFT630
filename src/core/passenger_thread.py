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

class PassengerThread(BaseComponentThread):
    def __init__(self, passenger, stop_event):
        super().__init__(passenger, stop_event, f"Passenger-{passenger.name}")
        
    def run(self):
        while not self.stop_event.is_set():
            try:
                # Log détaillé de l'état actuel
                self.logger.info(
                    f"👤 Passager {self.component.name} - Status: {self.component.status}, "
                    f"Position: {self._get_location_info()}, "
                    f"Destination: {self.component.destination.name if self.component.destination else 'Inconnue'}"
                )

                if self.component.status == "waiting":
                    self._try_board_bus()
                elif self.component.status == "in_bus":
                    self._check_arrival()
                elif self.component.status == "arrived":
                    self.logger.info(f"✅ Passager {self.component.name} arrivé à destination")
                    break

            except Exception as e:
                self.logger.error(f"Erreur pour passager {self.component.name}: {str(e)}")

            self.sleep_random(2, 4)

    def _try_board_bus(self):
        """Tente de monter dans un bus approprié"""
        if not self.component.current_stop:
            self.logger.warning(f"Passager {self.component.name} n'a pas d'arrêt actuel")
            return

        # Log des bus disponibles
        current_buses = self.component.current_stop.get_current_buses()
        if current_buses:
            self.logger.info(f"Bus disponibles à l'arrêt {self.component.current_stop.name}: {[bus.id for bus in current_buses]}")

        for bus in current_buses:
            # Vérification détaillée de la compatibilité du bus
            can_board = self._can_board_bus(bus)
            
            if can_board:
                if self.component.board_bus(bus):
                    self.logger.info(
                        f"🎯 Passager {self.component.name} monte dans le bus {bus.id} "
                        f"à l'arrêt {self.component.current_stop.name}"
                    )
                    return
                else:
                    self.logger.warning(f"Échec de l'embarquement pour {self.component.name} dans le bus {bus.id}")

    def _can_board_bus(self, bus) -> bool:
        """Vérifie si le passager peut monter dans ce bus"""
        if not bus.current_route:
            self.logger.debug(f"Bus {bus.id} n'a pas de route")
            return False

        # Vérifier si le bus va vers la destination du passager
        stops_to_check = []
        if hasattr(self.component.destination, 'stop_list'):  # Si la destination est une station
            stops_to_check.extend(self.component.destination.stop_list)
        else:  # Si la destination est un arrêt
            stops_to_check.append(self.component.destination)

        # Vérifier si un des arrêts de destination est sur la route du bus
        route_stops = bus.current_route.stop_list
        current_stop_index = route_stops.index(bus.current_stop) if bus.current_stop in route_stops else -1
        
        for stop in stops_to_check:
            if stop in route_stops:
                stop_index = route_stops.index(stop)
                if current_stop_index < stop_index:
                    self.logger.info(
                        f"✓ Bus {bus.id} validé pour passager {self.component.name} "
                        f"(destination trouvée sur la route)"
                    )
                    return True

        return False

    def _check_arrival(self):
        """Vérifie si le passager doit descendre à l'arrêt actuel"""
        if not self.component.current_bus or not self.component.current_bus.current_stop:
            return

        current_stop = self.component.current_bus.current_stop
        should_alight = self._should_alight_at_stop(current_stop)

        if should_alight:
            if self.component.alight_bus(current_stop):
                self.logger.info(
                    f"🏁 Passager {self.component.name} descend à {current_stop.name} "
                    f"(destination atteinte)"
                )

    def _should_alight_at_stop(self, stop) -> bool:
        """Vérifie si le passager doit descendre à cet arrêt"""
        # Si l'arrêt est la destination
        if stop == self.component.destination:
            return True

        # Si la destination est une station, vérifier si l'arrêt en fait partie
        if hasattr(self.component.destination, 'stop_list'):
            if stop in self.component.destination.stop_list:
                return True

        return False

    def _get_location_info(self):
        """Retourne une description détaillée de la position actuelle"""
        if self.component.status == "waiting":
            return f"En attente à {self.component.current_stop.name}"
        elif self.component.status == "in_bus":
            bus = self.component.current_bus
            return (f"Dans le bus {bus.id} à l'arrêt {bus.current_stop.name if bus.current_stop else 'inconnu'}"
                   f" - Direction: {bus.current_route.origin_end.name if bus.current_route else 'inconnue'}")
        elif self.component.status == "arrived":
            return f"Arrivé à {self.component.destination.name}"
        return "Position inconnue"