# add_user_interactive.py
import psycopg2
import hashlib
import os
import getpass  # Für die sichere Passworteingabe
from dotenv import load_dotenv  # Zum Laden von Umgebungsvariablen (optional aber empfohlen)

# Lade Umgebungsvariablen aus einer .env Datei (optional)
# Erstelle eine .env Datei im gleichen Verzeichnis mit:
# LOCAL_DB_URL=postgresql://localhost/ai_assistant_competition
# load_dotenv()

# --- Konfiguration ---
# Entweder aus Umgebungsvariablen lesen oder direkt hier eintragen
# DB_CONNECTION_STRING = os.getenv("LOCAL_DB_URL")
DB_CONNECTION_STRING = "postgresql://localhost/ai_assistant_competition"  # Ersetze ggf. mit deinem Connection String


# --- Funktionen ---
def hash_password(password):
    """Hasht das Passwort mit SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def add_user_to_db(user_id, email, password_hash, group_id, academic_year, class_char):
    """Fügt einen Nutzer zur Datenbank hinzu."""
    conn = None
    try:
        print(f"Verbinde mit Datenbank...")  # Connection String nicht mehr ausgeben
        conn = psycopg2.connect(DB_CONNECTION_STRING)
        cur = conn.cursor()
        print("Verbindung erfolgreich.")

        # SQL-Befehl zum Einfügen des Nutzers
        sql = """
        INSERT INTO user_ (user_id, email, password, group_id, academic_year, class)
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        cur.execute(sql, (user_id, email, password_hash, group_id, academic_year, class_char))

        # Änderungen übernehmen
        conn.commit()
        print(f"Nutzer '{user_id}' erfolgreich hinzugefügt.")

        cur.close()
        return True  # Erfolg signalisieren
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Fehler beim Hinzufügen des Nutzers: {error}")
        if conn is not None:
            conn.rollback()  # Änderungen rückgängig machen bei Fehler
        return False  # Fehler signalisieren
    finally:
        if conn is not None:
            conn.close()
            print("Datenbankverbindung geschlossen.")


def get_user_input():
    """Fragt die Nutzerdaten interaktiv ab."""
    print("Bitte gib die Daten für den neuen Nutzer ein:")

    user_id = input("User ID (z.B. nova123456): ")
    email = input("E-Mail-Adresse: ")

    while True:
        plain_password = getpass.getpass("Passwort (wird nicht angezeigt): ")
        confirm_password = getpass.getpass("Passwort bestätigen: ")
        if plain_password == confirm_password:
            break
        else:
            print("Passwörter stimmen nicht überein. Bitte erneut eingeben.")

    while True:
        try:
            group_id_str = input("Gruppen ID (Zahl): ")
            group_id = int(group_id_str)
            break
        except ValueError:
            print("Ungültige Eingabe. Bitte eine ganze Zahl für die Gruppen ID eingeben.")

    while True:
        try:
            academic_year_str = input("Akademisches Jahr (z.B. 2024): ")
            academic_year = int(academic_year_str)
            break
        except ValueError:
            print("Ungültige Eingabe. Bitte eine ganze Zahl für das akademische Jahr eingeben.")

    while True:
        class_char = input("Klasse (ein Buchstabe, z.B. A): ")
        if len(class_char) == 1 and class_char.isalpha():
            class_char = class_char.upper()  # Sicherstellen, dass es Grossbuchstabe ist
            break
        else:
            print("Ungültige Eingabe. Bitte einen einzelnen Buchstaben für die Klasse eingeben.")

    return user_id, email, plain_password, group_id, academic_year, class_char


# --- Hauptlogik ---
if __name__ == "__main__":
    # Überprüfen, ob die Datenbankverbindung konfiguriert ist
    if not DB_CONNECTION_STRING:
        print("Fehler: Datenbankverbindungszeichenfolge (DB_CONNECTION_STRING) ist nicht konfiguriert.")
    else:
        # Nutzerdaten abfragen
        user_id_input, email_input, plain_password_input, group_id_input, academic_year_input, class_input = get_user_input()

        # Passwort hashen
        hashed_pw = hash_password(plain_password_input)
        print(f"\nPasswort für Nutzer '{user_id_input}' wird gehasht...")

        # Nutzer hinzufügen
        print("Versuche, Nutzer zur Datenbank hinzuzufügen...")
        add_user_to_db(
            user_id_input,
            email_input,
            hashed_pw,
            group_id_input,
            academic_year_input,
            class_input
        )