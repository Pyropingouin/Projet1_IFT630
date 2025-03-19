import threading
import logging
import time
import random


class MutexSyncManager:
    def __init__(self, seed, monitor, perf_monitor):
        """
        Initialise le gestionnaire de synchronisation Mutex.

        Args:
            seed: Instance de STSSeed contenant les ressources.
            monitor: Moniteur de synchronisation (non utilisé dans cette version).
            perf_monitor: Moniteur de performance (non utilisé dans cette version).
        """
        self.seed = seed
        self.monitor = monitor
        self.perf_monitor = perf_monitor

        self.card_locks = {}  # Mutex pour les cartes
        self.card_balances = {}  # Soldes des cartes
        self.stop_locks = {}  # Mutex pour les arrêts
        self.stop_event = threading.Event()  # Pour arrêter la simulation proprement

    def initialize(self):
        """
        Initialise les mutex et les soldes des cartes des passagers ainsi que les mutex des arrêts.
        """
        logging.info("Initialisation des mutex et des soldes des cartes.")

        try:
            # Initialisation des cartes des passagers
            for passenger_id in self.seed.passengers.keys():
                self.card_locks[passenger_id] = threading.Lock()
                self.card_balances[passenger_id] = random.uniform(10, 100)  # Solde aléatoire entre 10 et 100

            # Initialisation des arrêts de bus
            for stop_id in self.seed.stops.keys():
                self.stop_locks[stop_id] = threading.Lock()

            logging.info(" Initialisation terminée.")

        except Exception as e:
            logging.error(f" Erreur pendant l'initialisation : {e}")
            raise RuntimeError("Échec de l'initialisation du gestionnaire de synchronisation") from e


    
      


    def pay_fare(self, passenger_id, amount=3.50) -> bool:

        if passenger_id not in self.card_balances:
            logging.warning(f"Passager {passenger_id} inconnu.")
            return False

        lock = self.card_locks.get(passenger_id)  # Récupérer le mutex du passager

        if lock is None:
            logging.warning(f"Aucun mutex pour le passager {passenger_id}.")
            return False

        if lock.acquire(timeout=2):  # Timeout ajouté
                try:
                    if self.card_balances[passenger_id] < amount:
                        logging.warning(f"Solde insuffisant pour le passager {passenger_id}.")
                        return False

                    self.card_balances[passenger_id] -= amount
                    logging.info(f"Paiement de {amount:.2f}$ réussi pour {passenger_id}. Solde restant: {self.card_balances[passenger_id]:.2f}$")
                    return True
                finally:
                    lock.release()
        else:
            logging.warning(f"Timeout : Carte du passager {passenger_id} inaccessible.")
            return False
                

    def recharge_card(self, passenger_id, amount) ->bool:

        if passenger_id not in self.card_balances:
            logging.warning(f"Passager {passenger_id} inconnu.")
            return False

        lock = self.card_locks.get(passenger_id)  # Récupérer le mutex du passager

        if lock.acquire(timeout=2):
            try:
                self.card_balances[passenger_id] += amount
                logging.info(f"Recharge de {amount:.2f}$ effectuée pour {passenger_id}. Nouveau solde: {self.card_balances[passenger_id]:.2f}$")
                return True
            finally:
                lock.release()
        else:
            logging.warning(f"Timeout : Carte du passager {passenger_id} inaccessible.")
            return False
        

    def refund(self, passenger_id, amount)->bool:
        if passenger_id not in self.card_balances:
            logging.warning(f"Passager {passenger_id} inconnu.")
            return False

        lock = self.card_locks.get(passenger_id)  # Récupérer le mutex du passager

        if lock is None:
            logging.warning(f"Aucun mutex pour le passager {passenger_id}.")
            return False
        
        with lock.aquire(timeout=2):
            try:
                self.card_balances[passenger_id] += amount
                return True
            finally:
                lock.release()
        

    def buy_monthly_pass(self, passenger_id) -> bool:
        PASS_COST = 45.0  

        if passenger_id not in self.card_balances:
            logging.warning(f"Passager {passenger_id} inconnu.")
            return False

        lock = self.card_locks.get(passenger_id)
        if lock is None:
            logging.warning(f"Aucun mutex pour le passager {passenger_id}.")
            return False

        if lock.acquire(timeout=2):
            try:
                if self.card_balances[passenger_id] < PASS_COST:
                    logging.warning(f"Solde insuffisant pour l'achat du pass mensuel pour {passenger_id}.")
                    return False

                self.card_balances[passenger_id] -= PASS_COST
                logging.info(f"Pass mensuel acheté pour {passenger_id}. Solde restant: {self.card_balances[passenger_id]:.2f}$")
                return True
            finally:
                lock.release()
        else:
            logging.warning(f"Timeout : Carte du passager {passenger_id} inaccessible.")
            return False



    def board_passenger(self, stop, buss, worker_id = None) -> bool:

        if stop not in self.stop_locks:
            logging.warning(f"Arrêt {stop} inconnu.")
            return False

        lock = self.stop_locks[stop]

        if lock.acquire(timeout=2):  # Utilisation d'un timeout pour éviter un blocage
            try:
                logging.info(f"Worker {worker_id} : Bus {bus} à l'arrêt {stop} - Montée des passagers en cours...")
                time.sleep(1)  # Simulation du temps nécessaire pour monter les passagers
                logging.info(f"Worker {worker_id} : Bus {bus} a terminé la montée des passagers à l'arrêt {stop}.")
                return True
            finally:
                lock.release()  # Libération du mutex après l'opération
        else:
            logging.warning(f"Worker {worker_id} : Timeout - L'arrêt {stop} est déjà en cours d'utilisation.")
            return False

    def alight_passengers(self, stop, bus, worker_id=None) -> bool:    

        if stop not in self.stop_locks:
            logging.warning(f"Arrêt {stop} inconnu.")
            return False

        lock = self.stop_locks[stop]

        if lock.acquire(timeout=2):  # Timeout pour éviter les blocages
            try:
                logging.info(f"Worker {worker_id} : Bus {bus} à l'arrêt {stop} - Descente des passagers en cours...")
                time.sleep(1)  # Simulation du temps de descente
                logging.info(f"Worker {worker_id} : Bus {bus} a terminé la descente des passagers à l'arrêt {stop}.")
                return True
            finally:
                lock.release()  # Libération du mutex après l'opération
        else:
            logging.warning(f"Worker {worker_id} : Timeout - L'arrêt {stop} est déjà utilisé pour une autre opération.")
            return False
       


   

    def run_scenarios(self, duration):
        """
        Exécute les scénarios de test en parallèle pour une durée donnée.

        Args:
            duration (int): Durée d'exécution en secondes.
        """
        logging.info("Démarrage de la simulation.")

        # Réinitialisation du signal d'arrêt
        self.stop_event.clear()

        # Création des threads pour chaque type de scénario
        threads = []

        # Ajout d'un thread pour simuler les transactions de cartes
        threads.append(threading.Thread(target=self.run_card_transactions_scenario))

        # Ajout d'un thread pour simuler les montées de passagers
        threads.append(threading.Thread(target=self.run_boarding_operations_scenario))

        # Ajout d'un thread pour simuler les descentes de passagers
        threads.append(threading.Thread(target=self.run_alighting_operations_scenario))

        # Démarrage de tous les threads
        for t in threads:
            t.start()

        # Attente pendant la durée spécifiée
        time.sleep(duration)

        # Arrêt des threads en activant le signal d'arrêt
        self.stop_event.set()

        # Attente de la fin des threads
        for t in threads:
            t.join()

        logging.info("Simulation terminée.")


def cleanup(self):
        """
        Libère les ressources utilisées par MutexSyncManager.

        Returns:
            bool: True si le nettoyage réussit, False sinon.
        """
        try:
            logging.info("🧹 Nettoyage des ressources par MutexSyncManager.")
            self.card_locks.clear()
            self.stop_locks.clear()
            self.card_balances.clear()
            logging.info(" MutexSyncManager nettoyé avec succès.")
            return True
        except Exception as e:
            logging.error(f" Erreur lors du nettoyage : {e}")
            return False