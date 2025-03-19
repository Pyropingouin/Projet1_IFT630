"""
Module: message_integration.py
---------------------------
Intégration du système de messagerie dans la simulation STS.

Montre comment intégrer le broker de messages dans la simulation
existante pour faciliter la communication entre composants.

Classes:
    MessageSimulationManager: Extension du SimulationManager avec messagerie

Auteur: [Votre Nom]
"""

import logging
import time
from typing import Dict, List, Set
from threading import Event

from src.seed.stsseed import STSSeed
from src.projects.project_0.simulations.simulation_manager import SimulationManager
from src.projects.project_2.core.message_broker import MessageBroker, MessageType, Message
from src.projects.project_2.core.message_components import MessageBusAdapter, MessageStopAdapter


class MessageSimulationManager:
    """Gestionnaire de simulation utilisant le système de messagerie"""
    
    def __init__(self, seed: STSSeed, duration: int = 60):
        """
        Initialise le gestionnaire de simulation
        
        Args:
            seed: Instance de STSSeed avec les données du réseau
            duration: Durée de la simulation en secondes
        """
        self.seed = seed
        self.duration = duration
        self.stop_event = Event()
        self.logger = logging.getLogger("message_simulation")
        
        # Initialisation du broker de messages
        self.message_broker = MessageBroker()
        
        # Adaptateurs pour les composants
        self.bus_adapters: Dict[int, MessageBusAdapter] = {}
        self.stop_adapters: Dict[str, MessageStopAdapter] = {}
        
        # Gestionnaire de simulation standard
        self.base_simulation = SimulationManager(seed, duration)
    
    def initialize(self) -> bool:
        """
        Initialise la simulation avec le système de messagerie
        
        Returns:
            bool: True si l'initialisation est réussie, False sinon
        """
        try:
            self.logger.info("Initialisation de la simulation avec messagerie...")
            
            # Création des adaptateurs pour les bus
            for bus_id, bus in self.seed.buses.items():
                self.bus_adapters[bus_id] = MessageBusAdapter(bus)
                self.logger.info(f"Adaptateur créé pour Bus-{bus_id}")
            
            # Création des adaptateurs pour les arrêts
            for stop_name, stop in self.seed.stops.items():
                self.stop_adapters[stop_name] = MessageStopAdapter(stop)
                self.logger.info(f"Adaptateur créé pour Stop-{stop_name}")
            
            # Publier un message de démarrage système
            self.publish_system_alert("Démarrage du système", level="INFO", 
                                     details={"component_count": len(self.bus_adapters) + len(self.stop_adapters)})
            
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de l'initialisation: {e}")
            return False
    
    def start_simulation(self) -> bool:
        """
        Démarre la simulation
        
        Returns:
            bool: True si le démarrage est réussi, False sinon
        """
        try:
            # Initialiser le système de messagerie
            if not self.initialize():
                return False
            
            # Démarrer la simulation de base
            self.base_simulation.start_simulation()
            
            # Log du démarrage
            self.logger.info("Simulation avec messagerie démarrée")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur au démarrage: {e}")
            return False
    
    def stop_simulation(self) -> None:
        """Arrête la simulation et nettoie les ressources"""
        try:
            # Publier un message d'arrêt
            self.publish_system_alert("Arrêt du système", level="INFO")
            
            # Arrêter la simulation de base
            self.base_simulation.stop_simulation()
            
            # Arrêter le broker de messages
            self.message_broker.shutdown()
            
            self.logger.info("Simulation avec messagerie arrêtée")
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'arrêt: {e}")
    
    def publish_system_alert(self, message: str, level: str = "INFO", details: Dict = None) -> None:
        """
        Publie une alerte système
        
        Args:
            message: Texte de l'alerte
            level: Niveau d'alerte (INFO, WARNING, ERROR)
            details: Détails additionnels
        """
        system_message = Message(
            MessageType.SYSTEM_ALERT,
            "SystemManager",
            {
                'message': message,
                'level': level,
                'details': details or {}
            }
        )
        self.message_broker.publish(system_message)
    
    @staticmethod
    def run(duration: int = 60) -> bool:
        """
        Lance une simulation complète avec messagerie
        
        Args:
            duration: Durée de la simulation en secondes
            
        Returns:
            bool: True si la simulation s'est correctement exécutée
        """
        # Initialisation du système
        seed = STSSeed()
        if not seed.initialize_system():
            logging.error("Échec de l'initialisation du système")
            return False
        
        # Création du gestionnaire de simulation
        simulation = MessageSimulationManager(seed, duration)
        
        try:
            # Démarrage de la simulation
            if not simulation.start_simulation():
                return False
            
            # Attente pendant la durée spécifiée
            logging.info(f"Simulation en cours pour {duration} secondes...")
            start_time = time.time()
            while (time.time() - start_time) < duration and not simulation.stop_event.is_set():
                time.sleep(1)
                
            # Succès
            return True
            
        except KeyboardInterrupt:
            logging.warning("Simulation interrompue par l'utilisateur")
            return False
            
        finally:
            # Nettoyage
            simulation.stop_simulation()


if __name__ == "__main__":
    # Configuration du logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Exécution de la simulation
    MessageSimulationManager.run(duration=60)