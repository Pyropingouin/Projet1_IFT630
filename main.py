import argparse
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
from src.projects.project_0.simulations.simulation_0 import Simulation0
from src.projects.project_1.simulations.simulation_1 import Simulation1
        

def run_simulation(sim_number: int, duration: int = 60) -> None:
    """
    Execute une simulation spécifique
    Args:
        sim_number: Numéro de la simulation à exécuter
        duration: Durée de la simulation en secondes
    """
    print(f"\nDémarrage de la simulation {sim_number}")
    print("=" * 50)

    if sim_number == 0:
        Simulation0.run(duration)
    elif sim_number == 1:
        Simulation1.run_simulation_1(duration)
    else:
        print(f"La simulation {sim_number} n'est pas encore prête")

def run_all_simulations(duration: int = 60) -> None:
    """
    Execute toutes les simulations séquentiellement
    Args:
        duration: Durée de chaque simulation en secondes
    """
    for i in range(4):  # Pour les simulations 0 à 3
        run_simulation(i, duration)

def main():
    parser = argparse.ArgumentParser(description='Exécution des simulations STS')
    parser.add_argument('--sim', type=int, choices=[0, 1, 2, 3], 
                      help='Numéro de la simulation à exécuter (0-3)')
    parser.add_argument('--duration', type=int, default=60,
                      help='Durée de la simulation en secondes (défaut: 60)')
    args = parser.parse_args()

    if args.sim is not None:
        run_simulation(args.sim, args.duration)
    else:
        run_all_simulations(args.duration)

if __name__ == "__main__":
    main()


