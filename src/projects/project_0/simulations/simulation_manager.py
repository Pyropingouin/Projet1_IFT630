"""
Module: simulation_manager.py
---------------------------
Gestionnaire principal de la simulation du réseau STS.

Coordonne l'exécution des différents threads de la simulation,
gère le cycle de vie des composants et assure la journalisation
des événements.

Classes:
    SimulationManager: Gestionnaire de la simulation

Dépendances:
    - threading
    - logging
    - colorama
    - models.*

Auteur: Hubert Ngankam
Email: hubert.ngankam@usherbrooke.ca
Session: H2025
Cours: IFT630
Version: 1.0
"""

from threading import Event
import logging
import sys
from datetime import datetime
from pathlib import Path

from src.core.bus_thread import BusThread
from src.core.passenger_thread import PassengerThread
from src.core.intersection_thread import IntersectionThread
from src.core.station_thread import StationThread
from src.core.stop_thread import StopThread
from ui.console_ui import ConsoleUI

from src.ui.console_ui import ConsoleUI
from src.ui.formatter import ColoredFormatter, FileFormatter

class SimulationManager:
    """Gestionnaire de la simulation du réseau STS"""
    
    def __init__(self, seed, duration=60):
        self.seed = seed
        self.duration = duration
        self.stop_event = Event()
        self.threads = []
        
        # Configuration du logging
        self._setup_logging()

    def _setup_logging(self):
        """Configure le système de logging"""
        # Création du logger principal
        self.logger = logging.getLogger('simulation')
        self.logger.setLevel(logging.INFO)
        
        # Suppression des handlers existants
        self.logger.handlers.clear()
        
        # Création du dossier logs s'il n'existe pas
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Nom du fichier de log avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = log_dir / f"simulation_{timestamp}.log"
        
        # Handler pour la console (coloré)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(ColoredFormatter())
        self.logger.addHandler(console_handler)
        
        # Handler pour le fichier
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(FileFormatter())
        self.logger.addHandler(file_handler)
        
        self.logger.info(f"Démarrage de la journalisation - Fichier: {self.log_file}")

    def start_simulation(self):
        """Démarre tous les threads de la simulation"""
        ConsoleUI.print_header()
        ConsoleUI.print_stats(self.seed)
        
        self._create_all_threads()
        
        # Démarrage des threads
        for thread in self.threads:
            thread.start()
            
        self.logger.info("✨ Simulation démarrée")

    def stop_simulation(self):
        """Arrête tous les threads de la simulation"""
        self.stop_event.set()
        for thread in self.threads:
            thread.join()
        self.logger.info("🏁 Simulation arrêtée")
        self.logger.info(f"Les logs sont disponibles dans: {self.log_file}")

    def _create_all_threads(self):
        """Crée tous les threads des composants"""
        self._create_passenger_threads()
        self._create_bus_threads()
        self._create_stop_threads()
        self._create_station_threads()
        self._create_intersection_threads()

    def _create_passenger_threads(self):
        self.logger.info("Création des threads passagers...")
        for passenger in self.seed.passengers.values():
            self.threads.append(PassengerThread(passenger, self.stop_event))

    def _create_bus_threads(self):
        self.logger.info("Création des threads bus...")
        for bus in self.seed.buses.values():
            self.threads.append(BusThread(bus, self.stop_event))

    def _create_stop_threads(self):
        self.logger.info("Création des threads arrêts...")
        for stop in self.seed.stops.values():
            self.threads.append(StopThread(stop, self.stop_event))

    def _create_station_threads(self):
        self.logger.info("Création des threads stations...")
        for station in self.seed.stations.values():
            self.threads.append(StationThread(station, self.stop_event))

    def _create_intersection_threads(self):
        self.logger.info("Création des threads intersections...")
        for intersection in self.seed.intersections.values():
            self.threads.append(IntersectionThread(intersection, self.stop_event))