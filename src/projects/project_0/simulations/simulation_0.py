"""
Module: simulation0.py
---------------------
Point d'entrée principal de la simulation du réseau STS.

Lance une simulation non synchronisée du réseau de transport
pour observer les interactions entre les composants.

Classes:
    Simulation0: Classe principale de la simulation

Utilisation:
    python simulation0.py [durée_en_secondes]

Arguments:
    durée_en_secondes : Durée de la simulation (défaut: 60)

Auteur: Hubert Ngankam
Email: hubert.ngankam@usherbrooke.ca
Session: H2025
Cours: IFT630
Version: 1.0
"""
import time
from src.seed.stsseed import STSSeed
from src.projects.project_0.simulations.simulation_manager import SimulationManager
from src.ui.console_ui import ConsoleUI

class Simulation0:
    @staticmethod
    def run(duration=60):
        """Lance la simulation pour une durée donnée"""
        try:
            # Initialisation du système
            seed = STSSeed()
            if not seed.initialize_system():
                ConsoleUI.print_error("Erreur lors de l'initialisation du système")
                return

            # Création et démarrage du gestionnaire de simulation
            simulation = SimulationManager(seed, duration)
            
            try:
                simulation.start_simulation()
                ConsoleUI.print_simulation_start()
                
                # Attente pendant la durée spécifiée
                start_time = time.time()
                while (time.time() - start_time) < duration:
                    remaining = duration - (time.time() - start_time)
                    ConsoleUI.print_simulation_time(remaining)
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                ConsoleUI.print_warning("Arrêt de la simulation demandé...")
            finally:
                simulation.stop_simulation()
                ConsoleUI.print_simulation_end()
                
        except Exception as e:
            ConsoleUI.print_error(str(e))
            raise