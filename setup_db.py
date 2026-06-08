import sqlite3
import os

def create_dummy_db():
    # Speichert die Datenbank im storage-Ordner
    os.makedirs("storage", exist_ok=True)
    conn = sqlite3.connect("storage/inventory.db")
    cursor = conn.cursor()

    # Tabelle erstellen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS parts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            part_name TEXT UNIQUE,
            stock_level INTEGER,
            price_per_unit REAL
        )
    ''')

    # Dummy-Daten (typische Bauteile) einfügen
    dummy_data = [
        ("Zylinderkopf TCD 2.9", 150, 450.00),
        ("Kurbelwelle V8", 12, 1200.50),
        ("Einspritzventil X-Serie", 850, 45.20),
        ("Ölfilter Standard", 5000, 12.99)
    ]

    # Daten einfügen
    cursor.executemany('''
        INSERT OR IGNORE INTO parts (part_name, stock_level, price_per_unit)
        VALUES (?, ?, ?)
    ''', dummy_data)

    conn.commit()
    conn.close()
    print("Datenbank 'inventory.db' wurde erfolgreich im Ordner 'storage' erstellt und gefüllt!")

if __name__ == "__main__":
    create_dummy_db()