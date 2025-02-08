"""
Module: formatters.py
--------------------
Formateurs personnalisés pour les logs de la simulation.

Fournit des classes de formatage pour la sortie console (colorée)
et la sortie fichier de la simulation.

Classes:
    ColoredFormatter: Formateur pour la sortie console avec couleurs
    FileFormatter: Formateur pour la sortie fichier

Auteur: Hubert Ngankam
Email: hubert.ngankam@usherbrooke.ca
Session: H2025
Cours: IFT630
Version: 1.0
"""

import logging
from datetime import datetime
import colorama
from colorama import Fore, Back, Style

# Initialisation de colorama pour Windows
colorama.init()

class ColoredFormatter(logging.Formatter):
    """Formateur personnalisé pour les logs colorés en console"""
    
    COLORS = {
        'Bus': Fore.GREEN,
        'Stop': Fore.YELLOW,
        'Station': Fore.BLUE,
        'Passenger': Fore.MAGENTA,
        'Intersection': Fore.CYAN,
        'System': Fore.WHITE,
        'ERROR': Fore.RED,
        'WARNING': Fore.YELLOW,
        'INFO': Fore.WHITE,
        'DEBUG': Fore.CYAN
    }
    
    def format(self, record):
        # Extraction du type d'entité depuis le nom du thread
        entity_type = record.threadName.split('-')[0] if '-' in record.threadName else 'System'
        
        # Sélection de la couleur
        color = self.COLORS.get(entity_type, Fore.WHITE)
        
        # Formatage de l'heure avec millisecondes
        time_str = datetime.fromtimestamp(record.created).strftime('%H:%M:%S.%f')[:-3]
        
        # Construction du message formaté
        formatted_message = (
            f"{Fore.WHITE}[{time_str}] "
            f"{color}{record.threadName}{Fore.WHITE}: "
            f"{color}{record.getMessage()}{Style.RESET_ALL}"
        )
        
        # Ajout des informations d'exception si présentes
        if record.exc_info:
            formatted_message += f"\n{Fore.RED}{self.formatException(record.exc_info)}{Style.RESET_ALL}"
            
        return formatted_message

class FileFormatter(logging.Formatter):
    """Formateur pour les logs dans le fichier"""
    
    def format(self, record):
        # Format détaillé pour le fichier de log
        time_str = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        formatted_message = (
            f"[{time_str}] [{record.threadName}] "
            f"[{record.levelname}]: {record.getMessage()}"
        )
        
        if record.exc_info:
            formatted_message += f"\nException: {self.formatException(record.exc_info)}"
            
        return formatted_message