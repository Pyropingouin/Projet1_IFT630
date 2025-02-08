"""
Module: console_ui.py
--------------------
Interface utilisateur en console pour la simulation du réseau STS.

Fournit des méthodes pour afficher les informations de la simulation
de manière formatée et colorée dans la console.

Classes:
    ConsoleUI: Gestionnaire d'interface console

Auteur: Hubert Ngankam
Email: hubert.ngankam@usherbrooke.ca
Session: H2025
Cours: IFT630
Version: 1.0
"""

import colorama
from colorama import Fore, Back, Style

# Initialisation de colorama pour Windows
colorama.init()

class ConsoleUI:
    """Classe pour gérer l'interface utilisateur en console"""
    
    @staticmethod
    def print_header():
        """Affiche l'en-tête de la simulation"""
        print("\n" + "="*80)
        print(f"{Fore.CYAN}STS NETWORK SIMULATION{Style.RESET_ALL}".center(80))
        print("="*80 + "\n")
    
    @staticmethod
    def print_stats(seed):
        """
        Affiche les statistiques du réseau
        
        Args:
            seed: Instance de STSSeed contenant les données du réseau
        """
        stats = [
            ("Stations", len(seed.stations), Fore.BLUE),
            ("Intersections", len(seed.intersections), Fore.CYAN),
            ("Arrêts", len(seed.stops), Fore.YELLOW),
            ("Bus", len(seed.buses), Fore.GREEN),
            ("Passagers", len(seed.passengers), Fore.MAGENTA)
        ]
        
        print("\n" + "-"*40)
        print(f"{Fore.WHITE}Statistiques du Réseau{Style.RESET_ALL}")
        print("-"*40)
        
        for name, count, color in stats:
            print(f"{color}{name}: {count}{Style.RESET_ALL}")
        
        print("-"*40 + "\n")
    
    @staticmethod
    def print_simulation_time(remaining_time):
        """
        Affiche le temps restant de la simulation
        
        Args:
            remaining_time: Temps restant en secondes
        """
        print(f"\r{Fore.YELLOW}Temps restant: {int(remaining_time)} secondes{Style.RESET_ALL}", 
              end='', flush=True)
    
    @staticmethod
    def print_simulation_start():
        """Affiche le message de démarrage de la simulation"""
        print(f"\n{Fore.GREEN}Démarrage de la simulation...{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Appuyez sur Ctrl+C pour arrêter la simulation{Style.RESET_ALL}\n")
    
    @staticmethod
    def print_simulation_end():
        """Affiche le message de fin de simulation"""
        print(f"\n{Fore.GREEN}Simulation terminée avec succès{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Consultez le dossier 'logs' pour l'analyse détaillée{Style.RESET_ALL}\n")
    
    @staticmethod
    def print_error(message):
        """
        Affiche un message d'erreur
        
        Args:
            message: Message d'erreur à afficher
        """
        print(f"\n{Fore.RED}Erreur: {message}{Style.RESET_ALL}\n")
    
    @staticmethod
    def print_warning(message):
        """
        Affiche un avertissement
        
        Args:
            message: Message d'avertissement à afficher
        """

        print(f"{Fore.YELLOW}Avertissement ⚠️ :{message}{Style.RESET_ALL}\n")
    
    @staticmethod
    def print_status_update(message, color=Fore.WHITE):
        """
        Affiche une mise à jour du statut
        
        Args:
            message: Message de statut à afficher
            color: Couleur du message (défaut: blanc)
        """
        print(f"{color}{message}{Style.RESET_ALL}\n")
    
    @staticmethod
    def print_success(message):
        """Affiche un message de succès"""
        print(f"{Fore.GREEN} Succès : ✓ {message}{Style.RESET_ALL}\n")