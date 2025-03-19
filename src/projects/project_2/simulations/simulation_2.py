"""
Module: simulation_2.py
---------------------
Point d'entrée pour la simulation utilisant le système de messagerie.

Lance une simulation du réseau STS avec communication par messages
entre les composants pour une meilleure coordination.

Classes:
    Simulation2: Classe principale de la simulation

Utilisation:
    python main.py --sim 2 [--duration 60]

Arguments:
    duration: Durée de la simulation en secondes (défaut: 60)

Auteur: [Votre Nom]
"""
import logging
from src.seed.stsseed import STSSeed
from src.projects.project_2.core.message_integration import MessageSimulationManager
from src.ui.console_ui import ConsoleUI

class Simulation2:
    @staticmethod
    def run(duration=60):
        """Lance la simulation avec messagerie pour une durée donnée"""
        try:
            # Affichage de l'en-tête
            ConsoleUI.print_header()
            ConsoleUI.print_status_update("Démarrage de la simulation avec messagerie...", "cyan")
            
            # Initialisation du système
            seed = STSSeed()
            if not seed.initialize_system():
                ConsoleUI.print_error("Échec de l'initialisation du système")
                return False
                
            # Affichage des statistiques
            ConsoleUI.print_stats(seed)
            
            # Création et démarrage du gestionnaire de simulation avec messagerie
            simulation = MessageSimulationManager(seed, duration)
            
            try:
                if not simulation.start_simulation():
                    ConsoleUI.print_error("Échec du démarrage de la simulation")
                    return False
                    
                ConsoleUI.print_simulation_start()
                
                # Attente pendant la durée spécifiée
                import time
                start_time = time.time()
                while (time.time() - start_time) < duration:
                    remaining = duration - (time.time() - start_time)
                    ConsoleUI.print_simulation_time(remaining)
                    time.sleep(1)
                    
                return True
                
            except KeyboardInterrupt:
                ConsoleUI.print_warning("Arrêt de la simulation demandé...")
                return False
                
            finally:
                # Toujours nettoyer correctement
                simulation.stop_simulation()
                ConsoleUI.print_simulation_end()
                
        except Exception as e:
            ConsoleUI.print_error(f"Erreur lors de la simulation: {str(e)}")
            logging.error(f"Erreur détaillée: {e}", exc_info=True)
            return False