"""
Module: logger_config.py
-----------------------
Configuration du système de journalisation pour la simulation.

Met en place la journalisation vers la console et les fichiers,
définit les formats et niveaux de log.

Fonctions:
    setup_logging: Configure le système de logging
    create_log_file: Crée un nouveau fichier de log
    get_logger: Récupère un logger configuré

Auteur: Hubert Ngankam
Email: hubert.ngankam@usherbrooke.ca
Session: H2025
Cours: IFT630
Version: 1.0
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from src.ui.formatter import ColoredFormatter, FileFormatter

def create_log_file():
    """Crée un nouveau fichier de log avec timestamp"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"simulation_{timestamp}.log"
    
    return log_file

def setup_logging(level=logging.INFO):
    """Configure le système de logging complet"""
    # Création du logger principal
    logger = logging.getLogger('simulation')
    logger.setLevel(level)
    
    # Suppression des handlers existants
    logger.handlers.clear()
    
    # Configuration du handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(ColoredFormatter())
    logger.addHandler(console_handler)
    
    # Configuration du handler fichier
    log_file = create_log_file()
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(FileFormatter())
    logger.addHandler(file_handler)
    
    # Log initial
    logger.info(f"Démarrage de la journalisation - Fichier: {log_file}")
    
    return logger, log_file

def get_logger(name='simulation'):
    """Récupère un logger configuré"""
    return logging.getLogger(name)

# Configuration des filtres pour éviter les messages de bibliothèques externes
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('matplotlib').setLevel(logging.WARNING)

# Exemple d'utilisation
if __name__ == '__main__':
    # Configuration initiale
    logger, log_file = setup_logging(logging.DEBUG)
    
    # Exemples de logs
    logger.debug("Message de debug")
    logger.info("Message d'information")
    logger.warning("Message d'avertissement")
    logger.error("Message d'erreur")
    
    # Exemple avec exception
    try:
        raise ValueError("Test d'exception")
    except Exception as e:
        logger.exception("Une erreur s'est produite")
        
    print(f"\nLogs enregistrés dans: {log_file}")