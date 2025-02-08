# Détection de Python
ifeq ($(shell python3 --version >/dev/null 2>&1; echo $$?),0)
    PYTHON = python3
else ifeq ($(shell python --version >/dev/null 2>&1; echo $$?),0)
    PYTHON = python
else
    $(error "Python non trouvé. Veuillez installer Python 3.x")
endif

# Variables d'environnement
VENV = .venv
VENV_BIN = $(VENV)/bin
ifeq ($(OS),Windows_NT)
    VENV_BIN = $(VENV)/Scripts
    PYTHON_VENV = $(VENV_BIN)/python.exe
    RM = rd /s /q
else
    PYTHON_VENV = $(VENV_BIN)/python
    RM = rm -rf
endif

SRC_DIR = src
TESTS_DIR = tests
DURATION = 60

.PHONY: all venv install clean lint format test run sim0 sim1 sim2 sim3 clean-venv help

# Afficher l'aide
help:
	@echo "Commandes disponibles:"
	@echo "  make venv          - Créer l'environnement virtuel"
	@echo "  make install       - Installer les dépendances"
	@echo "  make clean         - Nettoyer les fichiers générés"
	@echo "  make clean-venv    - Supprimer l'environnement virtuel"
	@echo "  make lint          - Vérifier le code"
	@echo "  make format        - Formater le code"
	@echo "  make test          - Lancer les tests"
	@echo "  make run          - Lancer toutes les simulations"
	@echo "  make sim0         - Lancer la simulation 0"
	@echo "  make sim1         - Lancer la simulation 1"
	@echo "  make sim2         - Lancer la simulation 2"
	@echo "  make sim3         - Lancer la simulation 3"
	@echo "  make val-sim0     - Lancer la validation de la simulation 0"
	@echo "  make val-sim1     - Lancer la validation de la simulation 1"
	@echo "  make val-sim2     - Lancer la validation de la simulation 2"
	@echo "  make val-sim3     - Lancer la validation de la simulation 3"

# Cible par défaut
all: venv install lint format run

# Créer l'environnement virtuel
venv:
	@echo "Création de l'environnement virtuel avec $(PYTHON)..."
	$(PYTHON) -m venv $(VENV)
	@echo "Environnement virtuel créé dans le dossier $(VENV)"
	@echo "Pour l'activer manuellement:"
ifeq ($(OS),Windows_NT)
	@echo "  $(VENV_BIN)/activate.bat"
else
	@echo "  source $(VENV_BIN)/activate"
endif

# Installation des dépendances dans l'environnement virtuel
install: venv
	@echo "Installation des dépendances..."
	$(PYTHON_VENV) -m pip install --upgrade pip
	$(PYTHON_VENV) -m pip install -r requirements.txt
	$(PYTHON_VENV) -m pip install flake8 pylint black pytest pytest-cov

# Nettoyage des fichiers générés
clean:
	@echo "Nettoyage des fichiers générés..."
	find . -type d -name "__pycache__" -exec $(RM) {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type f -name ".DS_Store" -delete
	find . -type d -name "*.egg-info" -exec $(RM) {} +
	find . -type d -name "*.egg" -exec $(RM) {} +
	find . -type d -name ".pytest_cache" -exec $(RM) {} +
	find . -type d -name ".mypy_cache" -exec $(RM) {} +
	find . -type d -name "htmlcov" -exec $(RM) {} +
	find . -type d -name "build" -exec $(RM) {} +
	find . -type d -name "dist" -exec $(RM) {} +
	find . -type d -name "logs" -exec $(RM) {} +

# Supprimer l'environnement virtuel
clean-venv:
	$(RM) $(VENV)

# Vérification de la qualité du code
lint:
	$(PYTHON_VENV) -m flake8 $(SRC_DIR) $(TESTS_DIR) --max-line-length=100
	$(PYTHON_VENV) -m pylint $(SRC_DIR) $(TESTS_DIR) --max-line-length=100

# Formatage du code
format:
	$(PYTHON_VENV) -m black $(SRC_DIR) $(TESTS_DIR) --line-length=100

# Exécution des tests
test:
	$(PYTHON_VENV) -m pytest $(TESTS_DIR) -v --cov=$(SRC_DIR)

# Simulations individuelles
sim0:
	$(PYTHON_VENV) main.py --sim 0 --duration $(DURATION)

sim1:
	$(PYTHON_VENV) main.py --sim 1 --duration $(DURATION)

sim2:
	$(PYTHON_VENV) main.py --sim 2 --duration $(DURATION)

sim3:
	$(PYTHON_VENV) main.py --sim 3 --duration $(DURATION)

# Lancement de toutes les simulations
run:
	$(PYTHON_VENV) main.py --duration $(DURATION)