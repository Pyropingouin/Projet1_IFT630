import threading
import logging


class SemaphoreSyncManager:  


    def __init__(self, seed, monitor, perf_monitor):
            """
            Initialise le gestionnaire de synchronisation basé sur les sémaphores.

            Args:
                seed: Instance de STSSeed contenant les ressources.
                monitor: Moniteur de synchronisation (non utilisé dans cette version).
                perf_monitor: Moniteur de performance (non utilisé dans cette version).
            """
            self.seed = seed
            self.monitor = monitor
            self.perf_monitor = perf_monitor

            # 1.1. Sémaphores pour les capacités des bus
            self.bus_semaphores = {}

            # 1.2. Sémaphores pour les arrêts (limiter le nombre de bus simultanés)
            self.stop_semaphores = {}

            # 1.3. Files d'attente des passagers par arrêt
            self.stop_queues = {}

            # 1.4. Verrous pour protéger l'accès aux files d'attente
            self.queue_locks = {}

    def initialize(self) -> bool:
        """
        Initialise les sémaphores pour les bus et les arrêts.

        Returns:
            bool: True si l'initialisation a réussi, False sinon.
        """
        logging.info(" Initialisation des sémaphores pour les bus et les arrêts.")

        try:
            # 2.1. Initialisation des sémaphores pour les capacités des bus
            for bus_id, bus in self.seed.buses.items():
                self.bus_semaphores[bus_id] = threading.Semaphore(bus.capacity)  # Capacité du bus
                logging.info(f" Bus {bus_id} : Capacité {bus.capacity} initialisée avec un sémaphore.")

            # 2.2. Initialisation des sémaphores pour les arrêts (limité à 2 bus max)
            for stop_id in self.seed.stops.keys():
                self.stop_semaphores[stop_id] = threading.Semaphore(2)  # Limite de 2 bus en même temps
                logging.info(f"Arrêt {stop_id} : Sémaphore de capacité 2 initialisé.")

            logging.info(" Initialisation des sémaphores terminée.")
            return True

        except Exception as e:
            logging.error(f" Erreur pendant l'initialisation des sémaphores : {e}")
            return False

            
    def board_passenger(self, bus_id, passenger_id, timeout=2.0) -> bool:
        """
        Fait monter un passager dans un bus si la capacité le permet.

        Args:
            bus_id (int): Identifiant du bus.
            passenger_id (int): Identifiant du passager.
            timeout (float): Délai d'attente maximum en secondes.

        Returns:
            bool: True si le passager a pu monter, False sinon.
        """
        if bus_id not in self.bus_semaphores:
            logging.warning(f"Bus {bus_id} introuvable.")
            return False

        bus_semaphore = self.bus_semaphores[bus_id]

        # 3.1. Acquisition du sémaphore avec timeout
        acquired = bus_semaphore.acquire(timeout=timeout)
        
        if not acquired:
            logging.info(f"Passager {passenger_id} n'a pas pu monter, bus {bus_id} plein.")
            return False  # Le passager ne peut pas monter

        # 3.2. Mise à jour de l'état du passager et du bus
        self.passenger_in_bus[passenger_id] = bus_id  # Associer le passager au bus
        logging.info(f"Passager {passenger_id} monte dans le bus {bus_id}.")
        
        return True


    def alight_passenger(self, bus_id, passenger_id) -> bool:
        """
        Fait descendre un passager d'un bus.

        Args:
            bus_id (int): Identifiant du bus.
            passenger_id (int): Identifiant du passager.

        Returns:
            bool: True si le passager a pu descendre, False sinon.
        """
        if bus_id not in self.bus_semaphores:
            logging.warning(f"Bus {bus_id} introuvable.")
            return False

        if passenger_id not in self.passenger_in_bus:
            logging.warning(f"Passager {passenger_id} introuvable dans un bus.")
            return False

        if self.passenger_in_bus[passenger_id] != bus_id:
            logging.warning(f"Passager {passenger_id} n'est pas dans le bus {bus_id}.")
            return False

        bus_semaphore = self.bus_semaphores[bus_id]

        try:
            # 3.3. Vérification que le passager est bien dans ce bus
            del self.passenger_in_bus[passenger_id]  # Retirer le passager du bus

            # 3.4. Mise à jour du sémaphore (libérer une place)
            bus_semaphore.release()
            logging.info(f"Passager {passenger_id} descend du bus {bus_id}.")
            return True
        except ValueError:
            logging.error(f"Erreur : tentative de libération en trop pour le bus {bus_id}.")
            return False


    def bus_arrive_at_stop(self, bus_id, stop_id, timeout=5.0) -> bool:
        """
        Gère l'arrivée d'un bus à un arrêt.

        Args:
            bus_id (int): Identifiant du bus.
            stop_id (int): Identifiant de l'arrêt.
            timeout (float): Délai d'attente maximum en secondes.

        Returns:
            bool: True si le bus a pu accéder à l'arrêt, False sinon.
        """
        if stop_id not in self.stop_semaphores:
            logging.warning(f"Arrêt {stop_id} introuvable.")
            return False

        stop_semaphore = self.stop_semaphores[stop_id]
        queue_lock = self.queue_locks[stop_id]
        stop_queue = self.stop_queues[stop_id]

        with queue_lock:
            stop_queue.append(bus_id)  # 4.1. Ajouter le bus à la file d'attente
            logging.info(f"Bus {bus_id} ajouté à la file d'attente de l'arrêt {stop_id}.")

        start_time = time.time()

        while True:
            with queue_lock:
                # 4.2. Attente active : Vérifie si le bus est en tête de la file
                if stop_queue[0] == bus_id:
                    break

            if time.time() - start_time > timeout:
                with queue_lock:
                    stop_queue.remove(bus_id)
                logging.warning(f"Bus {bus_id} a dépassé le délai d'attente et quitte la file.")
                return False

            time.sleep(0.1)  # Évite une boucle trop rapide

        # 4.3. Tente d'acquérir une place à l'arrêt
        if not stop_semaphore.acquire(timeout=timeout):
            with queue_lock:
                stop_queue.remove(bus_id)
            logging.warning(f"Bus {bus_id} n'a pas pu accéder à l'arrêt {stop_id}, arrêt plein.")
            return False

        with queue_lock:
            stop_queue.remove(bus_id)  # 4.3. Retirer le bus de la file d'attente

        # 4.4. Mise à jour de l'état du bus et de l'arrêt
        self.bus_at_stop[bus_id] = stop_id  # Associe le bus à l'arrêt
        self.stops_with_buses[stop_id].append(bus_id)  # 4.6. Ajout du bus à la liste des bus de l'arrêt

        logging.info(f"Bus {bus_id} est arrivé à l'arrêt {stop_id}.")
        return True

    def bus_depart_from_stop(self, bus_id, stop_id) -> bool:
        """
        Gère le départ d'un bus d'un arrêt.

        Args:
            bus_id (int): Identifiant du bus.
            stop_id (int): Identifiant de l'arrêt.

        Returns:
            bool: True si le bus a pu quitter l'arrêt, False sinon.
        """
        if stop_id not in self.stop_semaphores:
            logging.warning(f"Arrêt {stop_id} introuvable.")
            return False

        if bus_id not in self.bus_at_stop:
            logging.warning(f"Bus {bus_id} n'est pas enregistré à un arrêt.")
            return False

        if self.bus_at_stop[bus_id] != stop_id:
            logging.warning(f"Bus {bus_id} n'est pas actuellement à l'arrêt {stop_id}.")
            return False

        stop_semaphore = self.stop_semaphores[stop_id]
        
        try:
            stop_semaphore.release()  # 4.8. Libère une place à l'arrêt
            del self.bus_at_stop[bus_id]  # Supprime l'association bus/arrêt

            with self.queue_locks[stop_id]:
                self.stops_with_buses[stop_id].remove(bus_id)  # 4.9. Retrait du bus de l'arrêt

            logging.info(f"Bus {bus_id} a quitté l'arrêt {stop_id}.")
            return True
        except ValueError:
            logging.error(f"Erreur : tentative de libération en trop pour l'arrêt {stop_id}.")
            return False


    def run_scenarios(self, duration):
        """
        Exécute les scénarios de test.

        Args:
            duration (int): Durée d'exécution des scénarios en secondes.
        """
        logging.info("Démarrage des scénarios de test.")

        # 5.1. Création des threads pour les bus et passagers
        threads = []

        for bus_id in self.seed.buses.keys():
            thread = threading.Thread(target=self.simulate_bus, args=(bus_id,))
            threads.append(thread)

        for passenger_id in self.seed.passengers.keys():
            thread = threading.Thread(target=self.simulate_passenger, args=(passenger_id,))
            threads.append(thread)

        # 5.2. Démarrage des threads
        for thread in threads:
            thread.start()

        # 5.3. Attente de la fin des threads
        start_time = time.time()
        while time.time() - start_time < duration:
            time.sleep(1)  # Pause pour éviter de monopoliser le CPU

        # Arrêt de la simulation
        self.stop_event.set()

        for thread in threads:
            thread.join()  # Attente que tous les threads terminent leur exécution

        logging.info("Simulation terminée.")


    def cleanup(self):
        """
        Nettoie les ressources utilisées par SemaphoreSyncManager.

        Returns:
            bool: True si le nettoyage réussit, False sinon.
        """
        try:
            logging.info("🧹 Nettoyage des ressources.")
            self.bus_semaphores.clear()
            self.stop_semaphores.clear()
            self.stop_queues.clear()
            self.queue_locks.clear()
            self.bus_at_stop.clear()
            self.stops_with_buses.clear()
            logging.info(" Nettoyage terminé.")
            return True
        except Exception as e:
            logging.error(f" Erreur lors du nettoyage : {e}")
            return False
