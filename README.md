# Kalendarz z zadaniami (PySide6 + PostgreSQL przez SSH)

## Opis

Aplikacja okienkowa do zarządzania zadaniami z kalendarzem, obsługą wielu użytkowników, priorytetami, powtarzalnością i trybem jasnym/ciemnym. Zadania i użytkownicy są przechowywani w bazie PostgreSQL na zdalnym serwerze (połączenie przez SSH).

## Wymagania

- Python 3.10+
- Biblioteki: PySide6, sshtunnel, psycopg2-binary, python-dotenv
- Dostęp do serwera PostgreSQL przez SSH

## Instalacja zależności

W katalogu projektu uruchom:

```bash
pip install -r requirements.txt
```

Przykładowa zawartość requirements.txt:

```
PySide6
sshtunnel
psycopg2-binary
python-dotenv
```

## Konfiguracja

Uzupełnij plik `calendar.env` (w folderze `calendar/`):

```
SSH_HOST=adres.twojego.serwera
SSH_PORT=port_ssh
SSH_USER=nazwa_uzytkownika_ssh
SSH_PASSWORD=haslo_ssh
DB_HOST=127.0.0.1
DB_PORT=5432
DB_USER=nazwa_uzytkownika_bazy
DB_PASSWORD=haslo_bazy
DB_NAME=calendar_db
```

## Uruchomienie

W katalogu `pythonProject/window/calendar/`:

```bash
python calendar.py
```

## Budowanie aplikacji EXE (Windows)

1. Upewnij się, że masz plik `images/women.ico` (lub zmień ścieżkę w main.spec).
2. W katalogu z plikiem `main.spec` uruchom:

```bash
pyinstaller main.spec
```

3. Gotowy plik EXE znajdziesz w `build/main/` lub `dist/calendar/`.

## Funkcje

- Kalendarz z listą zadań na każdy dzień
- Filtrowanie zadań po statusie
- Priorytety, powtarzalność, deadline
- Obsługa wielu użytkowników (logowanie/rejestracja)
- Tryb jasny/ciemny
- Powiadomienia o zadaniach na dziś

## Struktura projektu

- `calendar.py` – główny plik aplikacji
- `task_manager.py` – obsługa bazy danych i użytkowników
- `task_list_dialog.py`, `task_detail_dialog.py` – okna dialogowe
- `login_dialog.py` – logowanie/rejestracja
- `calendar.env` – dane do połączenia z bazą
- `images/` – ikony

## Autor

fluktar


