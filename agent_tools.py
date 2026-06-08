import os
from unittest import result
from pypdf import PdfReader
import fitz
from langchain_core.tools import tool
import sqlite3
from typing import List

@tool
def read_pdf_document(file_path: str) -> str:
    """
    Ein Werkzeug, um den reinen Text aus einem lokalen PDF-Dokument auszulesen.
    Nutze dieses Werkzeug IMMER, wenn der User Fragen zum Inhalt einer spezifischen PDF-Datei stellt.
    Übergib den genauen Dateipfad (file_path) als Argument.
    """
    # Sicherheitscheck: Existiert die Datei überhaupt?
    if not os.path.exists(file_path):
        return f"System-Fehler: Das Dokument unter dem Pfad '{file_path}' wurde nicht gefunden."
    
    try:
        # PDF öffnen und Text Seite für Seite extrahieren
        reader = PdfReader(file_path)
        extracted_text = ""
        
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                extracted_text += f"\n--- Seite {page_num + 1} ---\n{text}"
                
        return extracted_text
    
    except Exception as e:
        return f"System-Fehler beim Lesen des PDFs: {str(e)}"
    
@tool
def highlight_pdf_text(file_path: str, search_terms: List[str]) -> str:
    """
    Ein Werkzeug, um EINE LISTE von wichtigen Textstellen oder Wörtern in einem PDF gelb zu markieren.
    Nutze dieses Werkzeug, wenn du selbstständig entschieden hast, welche Wörter/Zahlen wichtig sind, und übergebe sie als Liste.
    """
    if not os.path.exists(file_path):
        return f"Fehler: Datei '{file_path}' nicht gefunden."
    
    try:
        base_name = os.path.basename(file_path)
        
        # Falls der Agent aus Versehen schon den "highlighted_"-Pfad übergibt, bereinigen wir das
        clean_name = base_name.replace("highlighted_", "") if base_name.startswith("highlighted_") else base_name
            
        target_filename = f"highlighted_{clean_name}"
        target_path = os.path.join("storage", target_filename)
        
        # DER TRICK: Wenn es schon eine markierte Datei gibt, bauen wir auf dieser auf!
        file_to_open = target_path if os.path.exists(target_path) else file_path
        
        doc = fitz.open(file_to_open)
        total_matches = 0
        
        for page in doc:
            for search_text in search_terms:
                text_instances = page.search_for(search_text)
                for inst in text_instances:
                    highlight = page.add_highlight_annot(inst)
                    highlight.update()
                    total_matches += 1
                
        if total_matches == 0:
            doc.close()
            return "Ich konnte die gesuchten Begriffe im Dokument nicht finden."
            
        # Wir speichern in eine temporäre Datei, da PyMuPDF die geöffnete Datei nicht direkt überschreiben mag
        temp_path = os.path.join("storage", "temp_" + target_filename)
        doc.save(temp_path)
        doc.close()
        
        # Jetzt überschreiben wir die alte Datei mit unserer neuen Version inkl. ALLER Markierungen
        os.replace(temp_path, target_path)
        
        download_link = f"http://127.0.0.1:8000/download/{target_filename}"
        return f"Erfolg! Ich habe {total_matches} NEUE Markierungen zur Datei hinzugefügt. Link: {download_link}"
        
    except Exception as e:
        return f"Fehler beim Markieren des PDFs: {str(e)}"
@tool
def check_inventory_db(part_name: str) -> str:
    """
    Ein Werkzeug, um den aktuellen Lagerbestand und Preis eines Bauteils in der internen Datenbank abzufragen.
    Nutze dieses Tool IMMER, wenn der User fragt, ob wir etwas auf Lager haben oder was es kostet.
    Übergib den genauen Namen des Bauteils (part_name).
    """
    try:
        conn = sqlite3.connect("storage/inventory.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT part_name, stock_level, price_per_unit FROM parts WHERE part_name LIKE ?", (f"%{part_name}%",))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            name, stock, price = result
            return f"Datenbank-Eintrag gefunden: Wir haben {stock} Stück von '{name}' auf Lager. Der Stückpreis liegt bei {price} Euro."
        else:
            return f"Fehler: Das Bauteil '{part_name}' existiert nicht in unserer Datenbank."
            
    except Exception as e:
        return f"Datenbankfehler beim Abfragen: {str(e)}"

@tool
def update_inventory_db(part_name: str, quantity_change: int) -> str:
    """
    Ein Werkzeug, um den Lagerbestand in der Datenbank anzupassen (z.B. nach einer Bestellung oder Lieferung).
    Nutze dieses Tool, wenn der User sagt, dass neue Teile angekommen sind (positive Zahl) oder Teile entnommen wurden (negative Zahl).
    Übergib den Namen des Bauteils (part_name) und die Veränderung der Menge als ganze Zahl (quantity_change).
    """
    try:
        conn = sqlite3.connect("storage/inventory.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT stock_level FROM parts WHERE part_name LIKE ?", (f"%{part_name}%",))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            # hier ist ein tipp fur den ki agenten, 
            return f"Fehler: Bauteil '{part_name}' nicht gefunden. Wenn es sich um eine Neulieferung eines unbekannten Produkts handelt, benutze bitte das Tool 'add_new_inventory_item'."       
        current_stock = result[0]
        new_stock = current_stock + quantity_change
        
        cursor.execute("UPDATE parts SET stock_level = ? WHERE part_name LIKE ?", (new_stock, f"%{part_name}%"))
        conn.commit()
        conn.close()
        
        aktion = "hinzugefügt" if quantity_change > 0 else "entfernt"
        return f"Datenbank aktualisiert! Es wurden {abs(quantity_change)} Stück {aktion}. Der neue Lagerbestand für '{part_name}' ist jetzt {new_stock} Stück."
        
    except Exception as e:
        return f"Datenbankfehler beim Updaten: {str(e)}"
    
@tool
def delete_inventory_item(part_name: str) -> str:
    """
    Ein Werkzeug, um ein Bauteil KOMPLETT aus der Datenbank zu löschen.
    Nutze dieses Tool NUR, wenn der User explizit verlangt, dass ein Teil aus dem System, dem Sortiment oder der Datenbank entfernt wird.
    Übergib den Namen des Bauteils (part_name).
    """
    try:
        conn = sqlite3.connect("storage/inventory.db")
        cursor = conn.cursor()
        
        # Führe den echten SQL DELETE Befehl aus
        cursor.execute("DELETE FROM parts WHERE part_name LIKE ?", (f"%{part_name}%",))
        deleted_rows = cursor.rowcount # Zählt, wie viele Zeilen gelöscht wurden
        
        conn.commit()
        conn.close()
        
        if deleted_rows > 0:
            return f"Erfolg: Das Bauteil '{part_name}' wurde komplett aus der Datenbank gelöscht."
        else:
            return f"Fehler: Konnte '{part_name}' nicht löschen, da es nicht gefunden wurde."
            
    except Exception as e:
        return f"Datenbankfehler beim Löschen: {str(e)}"
    
@tool
def add_new_inventory_item(part_name: str, stock_level: int, price_per_unit: float) -> str:
    """
    Ein Werkzeug, um ein VÖLLIG NEUES Bauteil zum ersten Mal in die Datenbank aufzunehmen.
    Nutze dieses Tool NUR, wenn der User sagt, dass ein neues Produkt ins Sortiment aufgenommen wird.
    Übergib den Namen (part_name), den anfänglichen Bestand (stock_level) und den Preis pro Stück (price_per_unit).
    """

    try:
        conn = sqlite3.connect("storage/inventory.db")
        cursor = conn.cursor()
        
        # Prüfen, ob es vielleicht doch schon existiert
        cursor.execute("SELECT id FROM parts WHERE part_name = ?", (part_name,))
        if cursor.fetchone():
            conn.close()
            return f"Fehler: Das Bauteil '{part_name}' existiert bereits. Nutze stattdessen das Update-Tool."
            
        # Neues Bauteil einfügen
        cursor.execute('''
            INSERT INTO parts (part_name, stock_level, price_per_unit)
            VALUES (?, ?, ?)
        ''', (part_name, stock_level, price_per_unit))
        
        conn.commit()
        conn.close()
        
        return f"Erfolg: Das neue Bauteil '{part_name}' wurde mit einem Bestand von {stock_level} und einem Preis von {price_per_unit} Euro in die Datenbank aufgenommen."
        
    except Exception as e:
        return f"Datenbankfehler beim Hinzufügen: {str(e)}"