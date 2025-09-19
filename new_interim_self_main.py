import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random
import sqlite3


class MolekuelLernApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Molekül-Lern-App")
        self.root.geometry("1300x720")

        # Daten laden
        self.molekuele = self.lade_molekuele("molekuele_Gruppen.txt")
        self.aktueller_index = 0

        # Datenbank initialisieren
        self.initialisiere_datenbank()

        # Aktueller Modus
        self.aktueller_modus = "Üben"

        # Hauptcontainer erstellen
        self.main_container = tk.Frame(root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Seitliches Menü
        self.menu_frame = tk.Frame(self.main_container, width=250, bg="#f0f0f0",
                                   relief=tk.RAISED, borderwidth=1)
        self.menu_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.menu_frame.pack_propagate(False)

        # Menü-Titel
        tk.Label(self.menu_frame, text="Modi", font=("Arial", 14, "bold"),
                 bg="#f0f0f0").pack(pady=(20, 10))

        # Menü-Buttons
        self.ueben_btn = tk.Button(self.menu_frame, text="Üben", width=15,
                                   command=lambda: self.wechsle_modus("Üben"))
        self.ueben_btn.pack(pady=5)

        self.gewertet_btn = tk.Button(self.menu_frame, text="Gewertet", width=15,
                                      command=lambda: self.wechsle_modus("Gewertet"))
        self.gewertet_btn.pack(pady=5)

        self.training_btn = tk.Button(self.menu_frame, text="Training", width=15,
                                      command=lambda: self.wechsle_modus("Training"))
        self.training_btn.pack(pady=5)

        self.gruppen_btn = tk.Button(self.menu_frame, text="Gruppen", width=15,
                                     command=lambda: self.wechsle_modus("Gruppen"))
        self.gruppen_btn.pack(pady=5)

        self.namen_btn = tk.Button(self.menu_frame, text="Namen Lernen", width=15,
                                   command=lambda: self.wechsle_modus("Namen"))
        self.namen_btn.pack(pady=5)

        self.statistik_btn = tk.Button(self.menu_frame, text="Statistik", width=15,
                                       command=self.zeige_statistik)
        self.statistik_btn.pack(pady=5)


        # Suchleiste hinzufügen
        tk.Label(self.menu_frame, text="Molekül suchen:", bg="#f0f0f0").pack(pady=(20, 5))

        self.such_var = tk.StringVar()
        self.such_var.trace_add("write", self.aktualisiere_vorschlaege)
        self.such_eingabe = tk.Entry(self.menu_frame, textvariable=self.such_var, width=17)
        self.such_eingabe.pack(pady=5)

        # Vorschlagsfeld vorbereiten
        self.vorschlaege_listbox = tk.Listbox(self.menu_frame, width=17, height=6)
        self.vorschlaege_listbox.pack(pady=5)
        self.vorschlaege_listbox.bind("<<ListboxSelect>>", self.waehle_vorschlag)

        # Inhaltsbereich
        self.content_frame = tk.Frame(self.main_container)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # GUI-Elemente im Content-Bereich
        self.name_label = tk.Label(self.content_frame, text="", font=("Arial", 24))
        self.name_label.pack(pady=10)

        # Frame mit fester Höhe für das Bild
        self.bild_frame = tk.Frame(self.content_frame, height=450, width=750)
        self.bild_frame.pack_propagate(False)
        self.bild_frame.pack(pady=10)

        # Bild-Container innerhalb des Frames
        self.bild_container = tk.Label(self.bild_frame)
        self.bild_container.place(relx=0.5, rely=0.5, anchor="center")

        # Button-Frames für verschiedene Modi
        self.ueben_button_frame = tk.Frame(self.content_frame)
        self.gewertet_button_frame = tk.Frame(self.content_frame)

        # Buttons für Übungsmodus
        self.zeige_struktur_btn = tk.Button(self.ueben_button_frame, text="Struktur anzeigen",
                                            command=self.zeige_struktur)
        self.zeige_struktur_btn.grid(row=0, column=1, padx=10)

        self.vorheriges_btn = tk.Button(self.ueben_button_frame, text="Vorheriges",
                                        command=self.vorheriges_molekuel)
        self.vorheriges_btn.grid(row=0, column=0, padx=10)

        self.naechstes_btn = tk.Button(self.ueben_button_frame, text="Nächstes",
                                       command=self.naechstes_molekuel)
        self.naechstes_btn.grid(row=0, column=2, padx=10)

        self.zufaellig_btn = tk.Button(self.ueben_button_frame, text="Zufälliges Molekül",
                                       command=self.zufaelliges_molekuel)
        self.zufaellig_btn.grid(row=0, column=3, padx=10)

        # Buttons für Gewertet-Modus
        self.richtig_btn = tk.Button(self.gewertet_button_frame, text="Richtig ✓",
                                     command=lambda: self.bewerte_antwort(1), bg="#8fdf8f")
        self.richtig_btn.grid(row=0, column=0, padx=10)

        self.falsch_btn = tk.Button(self.gewertet_button_frame, text="Falsch ✗",
                                    command=lambda: self.bewerte_antwort(-1), bg="#ff9999")
        self.falsch_btn.grid(row=0, column=1, padx=10)

        self.ueberspringen_btn = tk.Button(self.gewertet_button_frame, text="Überspringen ↷",
                                           command=lambda: self.bewerte_antwort(0))
        self.ueberspringen_btn.grid(row=0, column=2, padx=10)

        self.struktur_gewertet_btn = tk.Button(self.gewertet_button_frame, text="Struktur anzeigen",
                                               command=self.zeige_struktur)
        self.struktur_gewertet_btn.grid(row=0, column=3, padx=10)

        # Neuen Button-Frame für den Namen-Lern-Modus erstellen
        self.namen_button_frame = tk.Frame(self.content_frame)

        # Buttons für Namen-Lern-Modus
        self.zeige_name_btn = tk.Button(self.namen_button_frame, text="Namen anzeigen",
                                        command=self.zeige_name)
        self.zeige_name_btn.grid(row=0, column=1, padx=10)

        self.vorheriges_namen_btn = tk.Button(self.namen_button_frame, text="Vorheriges",
                                              command=self.vorheriges_molekuel)
        self.vorheriges_namen_btn.grid(row=0, column=0, padx=10)

        self.naechstes_namen_btn = tk.Button(self.namen_button_frame, text="Nächstes",
                                             command=self.naechstes_molekuel)
        self.naechstes_namen_btn.grid(row=0, column=2, padx=10)

        self.zufaellig_namen_btn = tk.Button(self.namen_button_frame, text="Zufälliges Molekül",
                                             command=self.zufaelliges_molekuel)
        self.zufaellig_namen_btn.grid(row=0, column=3, padx=10)


        # Standard-Modus anzeigen
        self.wechsle_modus("Üben")

        # Erstes Molekül anzeigen
        self.aktuelles_bild = None
        self.zeige_aktuelles_molekuel()

    def lade_gruppen(self, dateiname="Gruppen.txt"):
        gruppen_dict = {}
        try:
            with open(dateiname, "r", encoding="utf-8") as datei:
                for zeile in datei:
                    zeile = zeile.strip()
                    if zeile:
                        teile = zeile.split(",")
                        if len(teile) >= 2:
                            gruppen_id = teile[0].strip()[:2]  # Ersten 2 Ziffern nehmen (xx)
                            gruppen_name = teile[1].strip()
                            gruppen_dict[gruppen_id] = gruppen_name
            return gruppen_dict
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Gruppendaten: {e}")
            return {}

    def lade_molekuele(self, dateiname):
        molekuele = []
        gruppen_dict = {}  # Dictionary für Gruppen-ID -> Gruppenname

        # Gruppennamen laden
        self.gruppen_dict = self.lade_gruppen()

        try:
            with open(dateiname, "r", encoding="utf-8") as datei:
                for zeile in datei:
                    zeile = zeile.strip()
                    if zeile:
                        teile = zeile.split(",")
                        if len(teile) >= 2:
                            nummer = teile[0].strip()
                            name = teile[1].strip()

                            # Gruppenindex ermitteln (erste 2 Ziffern)
                            gruppe_id = nummer[:2] if len(nummer) >= 2 else "00"

                            # Gruppennamen aus dem Dictionary holen oder Standard verwenden
                            gruppe_name = self.gruppen_dict.get(gruppe_id, f"Gruppe {gruppe_id}")

                            # Gruppenzuordnung speichern (für spätere Sortierung)
                            gruppen_dict[gruppe_id] = gruppe_name

                            # Bildnummer aus der Molekülnummer extrahieren (letzte 3 Ziffern)
                            bild_nummer = nummer[-3:].lstrip("0")
                            if not bild_nummer:  # Falls nur Nullen übrig bleiben
                                bild_nummer = "0"

                            molekuele.append({
                                "nummer": nummer,
                                "name": name,
                                "gruppe": gruppe_name,
                                "bild_nummer": bild_nummer
                            })

                # Gruppen nach Index sortieren statt alphabetisch
                self.verfuegbare_gruppen = [gruppen_dict[gruppe_id] for gruppe_id in sorted(gruppen_dict.keys())]
                return molekuele
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Laden der Moleküldaten: {e}")
            return []

    def zeige_aktuelles_molekuel(self):
        if not self.molekuele:
            self.name_label.config(text="Keine Moleküle gefunden")
            return

        molekuel = self.molekuele[self.aktueller_index]
        name = molekuel["name"]

        # Im Namen-Lern-Modus den Namen nicht anzeigen
        if self.aktueller_modus == "Namen":
            self.name_label.config(text="")
        # Im Gewertet-Modus auch den Score anzeigen
        elif self.aktueller_modus == "Gewertet":
            score, versuche = self.get_molekuel_score(molekuel["nummer"])
            self.name_label.config(text=f"{name}\nScore: {score:.2f} (Versuche: {versuche})")
        else:
            self.name_label.config(text=name)

        # Bild verstecken
        self.bild_container.config(image="")
        self.aktuelles_bild = None
        #Struktur anzeigen (außer im Namen-Lern-Modus, da wird sie separat gesteuert)
        if self.aktueller_modus == "Namen":
            self.zeige_struktur(zeige_name=False)  # Name wird bereits oben gesetzt

    def zeige_struktur(self, zeige_name=True):
        if not self.molekuele:
            return

        molekuel = self.molekuele[self.aktueller_index]
        # Hier die Bildnummer statt der Molekülnummer verwenden
        bild_nummer = molekuel.get("bild_nummer", molekuel["nummer"])
        bild_pfad = os.path.join("Bilder", f"{bild_nummer}.jpg")

        try:
            bild = Image.open(bild_pfad)

            # Konstante Höhe und maximale Breite festlegen
            ziel_hoehe = 400
            max_breite = 700  # Maximale Breite, die nicht überschritten werden soll

            # Seitenverhältnis berechnen und Breite entsprechend anpassen
            original_breite, original_hoehe = bild.size
            verhaeltnis = original_breite / original_hoehe
            ziel_breite = int(ziel_hoehe * verhaeltnis)

            # Wenn die Breite zu groß wird, passe stattdessen die Höhe an
            if ziel_breite > max_breite:
                ziel_breite = max_breite
                ziel_hoehe = int(ziel_breite / verhaeltnis)

            # Bild mit beibehaltenen Seitenverhältnissen skalieren
            bild = bild.resize((ziel_breite, ziel_hoehe), Image.LANCZOS)

            self.aktuelles_bild = ImageTk.PhotoImage(bild)
            self.bild_container.config(image=self.aktuelles_bild)

            if zeige_name and self.aktueller_modus != "Namen":
                self.name_label.config(text=molekuel["name"])

        except Exception as e:
            messagebox.showerror("Fehler", f"Bild konnte nicht geladen werden: {e}")

    def zeige_name(self):
        """Zeigt den Namen des aktuellen Moleküls im Namen-Lern-Modus an"""
        if not self.molekuele:
            return

        molekuel = self.molekuele[self.aktueller_index]
        name = molekuel["name"]

        # Namen im Label anzeigen
        self.name_label.config(text=name)

        # Button-Text ändern
        self.zeige_name_btn.config(text="Namen ausblenden", command=self.verstecke_name)

    def verstecke_name(self):
        """Versteckt den Namen im Namen-Lern-Modus"""
        # Namen ausblenden
        self.name_label.config(text="")

        # Button-Text zurücksetzen
        self.zeige_name_btn.config(text="Namen anzeigen", command=self.zeige_name)


    def naechstes_molekuel(self):
        """Zum nächsten Molekül wechseln (überschrieben für Training)"""
        if not self.molekuele:
            return

        if self.aktueller_modus == "Training" and hasattr(self, 'trainings_molekuele'):
            # Im Trainingsmodus durch die gefilterten Moleküle navigieren
            self.aktueller_trainings_index = (self.aktueller_trainings_index + 1) % len(self.trainings_molekuele)
            self.zeige_trainings_molekuel()
        elif self.aktueller_modus == "Gruppen" and hasattr(self, 'gruppen_molekuele'):
            # Im Gruppenmodus durch die Gruppenmoleküle navigieren
            self.aktueller_gruppen_index = (self.aktueller_gruppen_index + 1) % len(self.gruppen_molekuele)
            self.zeige_gruppen_molekuel()
        else:
            # Standardverhalten in anderen Modi
            self.aktueller_index = (self.aktueller_index + 1) % len(self.molekuele)
            self.zeige_aktuelles_molekuel()
            if self.aktueller_modus == "Namen":
                # Struktur im Namen-Lern-Modus sofort anzeigen
                self.name_label.config(text="")  # Namen ausblenden
                self.zeige_struktur(zeige_name=False)
                # Button zurücksetzen
                if hasattr(self, 'zeige_name_btn'):
                    self.zeige_name_btn.config(text="Namen anzeigen", command=self.zeige_name)

    def vorheriges_molekuel(self):
        """Zum vorherigen Molekül wechseln (überschrieben für Training)"""
        if not self.molekuele:
            return

        if self.aktueller_modus == "Training" and hasattr(self, 'trainings_molekuele'):
            # Im Trainingsmodus durch die gefilterten Moleküle navigieren
            self.aktueller_trainings_index = (self.aktueller_trainings_index - 1) % len(self.trainings_molekuele)
            self.zeige_trainings_molekuel()
        elif self.aktueller_modus == "Gruppen" and hasattr(self, 'gruppen_molekuele'):
            # Im Gruppenmodus durch die Gruppenmoleküle navigieren
            self.aktueller_gruppen_index = (self.aktueller_gruppen_index - 1) % len(self.gruppen_molekuele)
            self.zeige_gruppen_molekuel()
        else:
            # Standardverhalten in anderen Modi
            self.aktueller_index = (self.aktueller_index - 1) % len(self.molekuele)
            self.zeige_aktuelles_molekuel()
            if self.aktueller_modus == "Namen":
                # Struktur im Namen-Lern-Modus sofort anzeigen
                self.name_label.config(text="")  # Namen ausblenden
                self.zeige_struktur(zeige_name=False)
                # Button zurücksetzen
                if hasattr(self, 'zeige_name_btn'):
                    self.zeige_name_btn.config(text="Namen anzeigen", command=self.zeige_name)

    def zufaelliges_molekuel(self):
        if self.aktueller_modus == "Training" and hasattr(self, 'trainings_molekuele'):
            if not self.trainings_molekuele or len(self.trainings_molekuele) <= 1:
                return

            # Zufälligen Index aus der Trainings-Liste auswählen
            neuer_index = self.aktueller_trainings_index
            while neuer_index == self.aktueller_trainings_index:
                neuer_index = random.randint(0, len(self.trainings_molekuele) - 1)

            self.aktueller_trainings_index = neuer_index
            self.zeige_trainings_molekuel()

        elif self.aktueller_modus == "Gruppen" and hasattr(self, 'gruppen_molekuele'):
            if not self.gruppen_molekuele or len(self.gruppen_molekuele) <= 1:
                return

            # Zufälligen Index aus der Gruppen-Liste auswählen
            neuer_index = self.aktueller_gruppen_index
            while neuer_index == self.aktueller_gruppen_index:
                neuer_index = random.randint(0, len(self.gruppen_molekuele) - 1)

            self.aktueller_gruppen_index = neuer_index
            self.zeige_gruppen_molekuel()

        elif (self.aktueller_modus == "Gewertet" or self.aktueller_modus == "Üben" or self.aktueller_modus == "Namen") and hasattr(self, 'gruppen_checkboxes'):
            # Ausgewählte Gruppen ermitteln
            ausgewaehlte_gruppen = [gruppe for gruppe, var in self.gruppen_checkboxes.items() if var.get()]

            # Wenn keine Gruppen ausgewählt sind, eine Warnung anzeigen
            if not ausgewaehlte_gruppen:
                messagebox.showwarning("Keine Gruppen ausgewählt",
                                       "Bitte wähle mindestens eine Gruppe aus.")
                return

            # Nur Moleküle aus den ausgewählten Gruppen filtern
            gefilterte_molekuele = [m for m in self.molekuele if m["gruppe"] in ausgewaehlte_gruppen]

            if not gefilterte_molekuele or len(gefilterte_molekuele) <= 1:
                messagebox.showinfo("Hinweis", "Nicht genügend Moleküle in den ausgewählten Gruppen.")
                return

            # Zufälligen Index aus den gefilterten Molekülen auswählen
            aktuelles_molekuel = self.molekuele[self.aktueller_index]
            neuer_index = self.aktueller_index
            max_versuche = 100  # Verhindert Endlosschleife

            for _ in range(max_versuche):
                zufalls_molekuel = random.choice(gefilterte_molekuele)
                # Index in der Hauptliste finden
                for i, m in enumerate(self.molekuele):
                    if m["nummer"] == zufalls_molekuel["nummer"] and i != self.aktueller_index:
                        neuer_index = i
                        break

                # Wenn ein neues Molekül gefunden wurde, abbrechen
                if neuer_index != self.aktueller_index:
                    break

            self.aktueller_index = neuer_index
            self.zeige_aktuelles_molekuel()

        else:
            # Standardverhalten für andere Modi
            if not self.molekuele or len(self.molekuele) <= 1:
                return

            # Zufälligen Index auswählen (nicht den aktuellen)
            neuer_index = self.aktueller_index
            while neuer_index == self.aktueller_index:
                neuer_index = random.randint(0, len(self.molekuele) - 1)

            self.aktueller_index = neuer_index
            self.zeige_aktuelles_molekuel()

    def wechsle_modus(self, modus):
        self.aktueller_modus = modus

        # Alle Button-Frames ausblenden
        self.ueben_button_frame.pack_forget()
        self.gewertet_button_frame.pack_forget()
        self.namen_button_frame.pack_forget()

        # Gruppenauswahl-Panel ausblenden (falls vorhanden)
        if hasattr(self, 'gruppen_auswahl_frame'):
            self.gruppen_auswahl_frame.pack_forget()

        # Buttons hervorheben
        self.ueben_btn.config(relief=tk.RAISED)
        self.gewertet_btn.config(relief=tk.RAISED)
        self.namen_btn.config(relief=tk.RAISED)
        self.training_btn.config(relief=tk.RAISED)
        self.gruppen_btn.config(relief=tk.RAISED)

        # Molekülnamen ausblenden für Namen-Lern-Modus
        self.name_label.config(text="")

        # Entsprechenden Button-Frame anzeigen
        if modus == "Üben":
            self.ueben_button_frame.pack(pady=10)
            self.ueben_btn.config(relief=tk.SUNKEN)
            # Gruppenauswahl-Panel auch im Übe-Modus anzeigen
            self.erstelle_gruppenauswahl_panel()
            # Name anzeigen
            self.zeige_aktuelles_molekuel()

        elif modus == "Gewertet":
            self.gewertet_button_frame.pack(pady=10)
            self.gewertet_btn.config(relief=tk.SUNKEN)
            # Gruppenauswahl-Panel erstellen und anzeigen
            self.erstelle_gruppenauswahl_panel()
            # Name anzeigen
            self.zeige_aktuelles_molekuel()
            # Zufälliges Molekül beim Start des Gewertet-Modus
            if self.molekuele and len(self.molekuele) > 1:
                self.zufaelliges_molekuel()


        elif modus == "Namen":
            self.namen_button_frame.pack(pady=10)
            self.namen_btn.config(relief=tk.SUNKEN)
            # Gruppenauswahl-Panel anzeigen
            self.erstelle_gruppenauswahl_panel()
            # Name ausblenden
            self.name_label.config(text="")
            # Zufälliges Molekül und direkt die Struktur zeigen
            if self.molekuele and len(self.molekuele) > 1:
                self.zufaelliges_molekuel()
                # Explizit Struktur anzeigen ohne den Namen
                self.zeige_struktur(zeige_name=False)
            # Button zurücksetzen
            if hasattr(self, 'zeige_name_btn'):
                self.zeige_name_btn.config(text="Namen anzeigen", command=self.zeige_name)

        elif modus == "Training":
            # Training-Kategorie auswählen
            self.waehle_training_kategorie()
            self.training_btn.config(relief=tk.SUNKEN)
            # Training nutzt die gleichen Buttons wie Üben
            self.ueben_button_frame.pack(pady=10)

        elif modus == "Gruppen":
            # Gruppenauswahl anzeigen
            self.waehle_gruppe()
            self.gruppen_btn.config(relief=tk.SUNKEN)
            # Gruppen nutzen die gleichen Buttons wie Üben
            self.ueben_button_frame.pack(pady=10)

        # Aktuelles Molekül neu anzeigen
        self.zeige_aktuelles_molekuel()

    def waehle_training_kategorie(self):
        """Dialog zur Auswahl einer Trainingskategorie anzeigen"""
        kategorie_fenster = tk.Toplevel(self.root)
        kategorie_fenster.title("Trainingskategorie auswählen")
        kategorie_fenster.geometry("400x300")
        kategorie_fenster.transient(self.root)
        kategorie_fenster.grab_set()  # Modal machen

        tk.Label(kategorie_fenster, text="Welche Moleküle möchtest du trainieren?",
                 font=("Arial", 12, "bold")).pack(pady=(20, 30))

        # Kategorie-Variable
        self.training_kategorie = tk.StringVar()

        # Optionen
        optionen = [
            ("Katastrophe (Score < -0.66)", -0.66),
            ("Oh Gott (Score < 0.33)", 0.33),
            ("Meh (Score < 0)", 0),
            ("Das geht besser! (Score < 0.5)", 0.5)
        ]

        for text, wert in optionen:
            rb = tk.Radiobutton(kategorie_fenster, text=text, value=wert,
                                variable=self.training_kategorie, font=("Arial", 11))
            rb.pack(anchor=tk.W, padx=30, pady=5)

        # Standardwert setzen
        self.training_kategorie.set(-0.66)

        # Buttons
        button_frame = tk.Frame(kategorie_fenster)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Abbrechen",
                  command=lambda: self.wechsle_modus("Üben")).pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Starten",
                  command=lambda: [kategorie_fenster.destroy(), self.starte_training()]).pack(side=tk.LEFT, padx=10)

        # Warten, bis das Fenster geschlossen wird
        self.root.wait_window(kategorie_fenster)

    def starte_training(self):
        """Training mit den gefilterten Molekülen starten"""
        # Score-Schwellwert aus der Auswahl holen
        schwellwert = float(self.training_kategorie.get())

        # Moleküle mit niedrigem Score finden
        self.trainings_molekuele = []

        for molekuel in self.molekuele:
            score, _ = self.get_molekuel_score(molekuel["nummer"])
            if score < schwellwert:
                self.trainings_molekuele.append(molekuel)

        if not self.trainings_molekuele:
            messagebox.showinfo("Training", "Keine Moleküle gefunden, die dem Kriterium entsprechen!")
            self.wechsle_modus("Üben")
            return

        # Zufällige Reihenfolge für das Training
        random.shuffle(self.trainings_molekuele)

        # Erstes Molekül anzeigen
        self.aktueller_trainings_index = 0
        self.zeige_trainings_molekuel()

    def zeige_trainings_molekuel(self):
        """Aktuelles Trainingsmolekül anzeigen"""
        if not hasattr(self, 'trainings_molekuele') or not self.trainings_molekuele:
            return

        molekuel = self.trainings_molekuele[self.aktueller_trainings_index]

        # Entsprechendes Molekül im Hauptarray finden
        for i, m in enumerate(self.molekuele):
            if m["nummer"] == molekuel["nummer"]:
                self.aktueller_index = i
                break

        # Molekül anzeigen
        self.zeige_aktuelles_molekuel()

        # Zusätzlich Fortschritt anzeigen
        score, versuche = self.get_molekuel_score(molekuel["nummer"])
        gesamt = len(self.trainings_molekuele)
        aktuell = self.aktueller_trainings_index + 1

        self.name_label.config(text=f"{molekuel['name']}\n"
                                    f"Score: {score:.2f} (Versuche: {versuche})\n"
                                    f"Trainingsfortschritt: {aktuell}/{gesamt}")

    def initialisiere_datenbank(self):
        try:
            conn = sqlite3.connect("molekuel_scores.db")
            cursor = conn.cursor()

            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS molekuel_scores
                           (
                               molekuel_nummer
                               TEXT
                               PRIMARY
                               KEY,
                               score
                               REAL
                               DEFAULT
                               0,
                               versuche
                               INTEGER
                               DEFAULT
                               0
                           )
                           ''')

            # Moleküle in Datenbank eintragen falls nicht vorhanden
            for molekuel in self.molekuele:
                nummer = molekuel["nummer"]
                cursor.execute("SELECT * FROM molekuel_scores WHERE molekuel_nummer = ?", (nummer,))

                if not cursor.fetchone():
                    cursor.execute("INSERT INTO molekuel_scores (molekuel_nummer) VALUES (?)", (nummer,))

            conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Datenbankfehler", f"Fehler beim Initialisieren der Datenbank: {e}")


    def get_molekuel_score(self, molekuel_nummer):
        try:
            conn = sqlite3.connect("molekuel_scores.db")
            cursor = conn.cursor()

            cursor.execute("SELECT score, versuche FROM molekuel_scores WHERE molekuel_nummer = ?",
                           (molekuel_nummer,))
            result = cursor.fetchone()
            conn.close()

            if result:
                return result
            return 0, 0
        except Exception as e:
            messagebox.showerror("Datenbankfehler", f"Fehler beim Abrufen des Scores: {e}")
            return 0, 0


    def bewerte_antwort(self, wertung):
        if not self.molekuele:
            return

        molekuel = self.molekuele[self.aktueller_index]
        nummer = molekuel["nummer"]

        # Überspringen: keine Wertung
        if wertung == 0:
            if self.aktueller_modus == "Gewertet":
                self.zufaelliges_molekuel()
            else:
                self.naechstes_molekuel()
            return
        try:
            # Aktuellen Score und Versuche abrufen
            score, versuche = self.get_molekuel_score(nummer)

            # Neuen Score berechnen
            neuer_score = (score + wertung) / (versuche + 1)
            neue_versuche = versuche + 1

            # Score in Datenbank aktualisieren
            conn = sqlite3.connect("molekuel_scores.db")
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE molekuel_scores SET score = ?, versuche = ? WHERE molekuel_nummer = ?",
                (neuer_score, neue_versuche, nummer)
            )
            conn.commit()
            conn.close()

            # Feedback anzeigen
            #    if wertung > 0:
            #        messagebox.showinfo("Bewertung", f"Richtig! Neuer Score: {neuer_score:.2f}")
            #    else:
            #        messagebox.showinfo("Bewertung", f"Falsch! Neuer Score: {neuer_score:.2f}")

            # Zum nächsten Molekül
            if self.aktueller_modus == "Gewertet":
                self.zufaelliges_molekuel()
            else:
                self.naechstes_molekuel()

        except Exception as e:
            messagebox.showerror("Datenbankfehler", f"Fehler beim Aktualisieren des Scores: {e}")

    def zeige_statistik(self):
        # Neues Fenster erstellen
        statistik_fenster = tk.Toplevel(self.root)
        statistik_fenster.title("Molekül-Statistik")
        statistik_fenster.geometry("600x400")

        # Tabellen-Frame
        tabellen_frame = tk.Frame(statistik_fenster)
        tabellen_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tabelle erstellen
        from tkinter import ttk
        tabelle = ttk.Treeview(tabellen_frame, columns=("name", "score", "versuche"), show="headings")

        # Spalten definieren
        tabelle.heading("name", text="Molekül")
        tabelle.heading("score", text="Score",
                        command=lambda: self.sortiere_tabelle(tabelle, "score", False))
        tabelle.heading("versuche", text="Versuche",
                        command=lambda: self.sortiere_tabelle(tabelle, "versuche", False))

        tabelle.column("name", width=300)
        tabelle.column("score", width=150, anchor="center")
        tabelle.column("versuche", width=150, anchor="center")

        # Scrollbar hinzufügen
        scrollbar = ttk.Scrollbar(tabellen_frame, orient="vertical", command=tabelle.yview)
        tabelle.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tabelle.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Daten aus der Datenbank laden und in die Tabelle einfügen
        try:
            conn = sqlite3.connect("molekuel_scores.db")
            cursor = conn.cursor()
            cursor.execute("SELECT molekuel_nummer, score, versuche FROM molekuel_scores")
            alle_scores = cursor.fetchall()
            conn.close()

            molekuel_namen = {m["nummer"]: m["name"] for m in self.molekuele}

            # Durchschnittsscore berechnen
            gesamt_score = 0
            aktive_molekuele = 0

            # Daten in die Tabelle einfügen
            for nummer, score, versuche in alle_scores:
                name = molekuel_namen.get(nummer, f"Unbekannt ({nummer})")
                tabelle.insert("", "end", values=(name, f"{score:.2f}", versuche))

                # Nur Moleküle mit mindestens einem Versuch einbeziehen
                if versuche > 0:
                    gesamt_score += score
                    aktive_molekuele += 1

            # Durchschnitt berechnen
            durchschnitt = gesamt_score / aktive_molekuele if aktive_molekuele > 0 else 0

            # Initial nach Score sortieren (absteigend)
            self.sortiere_tabelle(tabelle, "score", False)

        except Exception as e:
            messagebox.showerror("Datenbankfehler", f"Fehler beim Laden der Statistik: {e}")
            durchschnitt = 0
            aktive_molekuele = 0

        # Frame für Zusammenfassung
        zusammenfassung_frame = tk.Frame(statistik_fenster)
        zusammenfassung_frame.pack(fill=tk.X, padx=10)

        # Durchschnittsscore anzeigen
        durchschnitt_label = tk.Label(
            zusammenfassung_frame,
            text=f"Durchschnittsscore: {durchschnitt:.2f} (aus {aktive_molekuele} Molekülen mit Versuchen)",
            font=("Arial", 10, "bold")
        )
        durchschnitt_label.pack(pady=10)

        # Button zum Schließen
        schliessen_btn = tk.Button(statistik_fenster, text="Schließen",
                                   command=statistik_fenster.destroy)
        schliessen_btn.pack(pady=5)

        zuruecksetzen_btn = tk.Button(statistik_fenster, text="Statistik zurücksetzen",
                                      command=lambda: self.statistik_zuruecksetzen(tabelle, durchschnitt_label))
        zuruecksetzen_btn.pack(pady=5)

    def sortiere_tabelle(self, tabelle, spalte, aufsteigend):
        # Alle Einträge aus der Tabelle holen
        daten = [(tabelle.set(kind, spalte), kind) for kind in tabelle.get_children("")]

        # Sortieren (numerisch für score und versuche)
        if spalte in ["score", "versuche"]:
            daten.sort(key=lambda x: float(x[0]), reverse=not aufsteigend)
        else:
            daten.sort(reverse=not aufsteigend)

        # Reihenfolge in der Tabelle aktualisieren
        for index, (val, kind) in enumerate(daten):
            tabelle.move(kind, "", index)

        # Sortierrichtung umkehren für den nächsten Klick
        tabelle.heading(spalte, command=lambda: self.sortiere_tabelle(tabelle, spalte, not aufsteigend))

    def statistik_zuruecksetzen(self, tabelle, durchschnitt_label=None):
        """Alle Scores und Versuche zurücksetzen"""
        bestaetigung = messagebox.askyesno(
            "Statistik zurücksetzen",
            "Möchtest du wirklich alle Scores und Versuche zurücksetzen? Diese Aktion kann nicht rückgängig gemacht werden.",
            icon=messagebox.WARNING
        )

        if not bestaetigung:
            return

        try:
            # Datenbank komplett neu initialisieren
            conn = sqlite3.connect("molekuel_scores.db")
            cursor = conn.cursor()

            # Alte Daten löschen
            cursor.execute("DELETE FROM molekuel_scores")

            # Moleküle mit neuen Nummern neu eintragen
            for molekuel in self.molekuele:
                nummer = molekuel["nummer"]
                cursor.execute("INSERT INTO molekuel_scores (molekuel_nummer, score, versuche) VALUES (?, 0, 0)",
                               (nummer,))

            conn.commit()
            conn.close()

            # Tabelle aktualisieren
            for item in tabelle.get_children():
                tabelle.delete(item)

            # Neu befüllen
            molekuel_namen = {m["nummer"]: m["name"] for m in self.molekuele}

            conn = sqlite3.connect("molekuel_scores.db")
            cursor = conn.cursor()
            cursor.execute("SELECT molekuel_nummer, score, versuche FROM molekuel_scores")
            alle_scores = cursor.fetchall()
            conn.close()

            for nummer, score, versuche in alle_scores:
                name = molekuel_namen.get(nummer, f"Unbekannt ({nummer})")
                tabelle.insert("", "end", values=(name, f"{score:.2f}", versuche))

            # Durchschnittslabel aktualisieren, falls vorhanden
            if durchschnitt_label:
                durchschnitt_label.config(text="Durchschnittsscore: 0.00 (aus 0 Molekülen mit Versuchen)")

            messagebox.showinfo("Statistik zurückgesetzt", "Alle Scores und Versuche wurden erfolgreich zurückgesetzt.")

        except Exception as e:
            messagebox.showerror("Datenbankfehler", f"Fehler beim Zurücksetzen der Statistik: {e}")

    def aktualisiere_vorschlaege(self, *args):
        suchtext = self.such_var.get().lower()

        # Vorschlagsliste leeren
        self.vorschlaege_listbox.delete(0, tk.END)

        if len(suchtext) < 2:
            return

        # Passende Moleküle finden
        for molekuel in self.molekuele:
            if suchtext in molekuel["name"].lower():
                self.vorschlaege_listbox.insert(tk.END, molekuel["name"])

                # Maximal 6 Vorschläge anzeigen
                if self.vorschlaege_listbox.size() >= 6:
                    break


    def waehle_vorschlag(self, event):
        # Auswahl prüfen
        if not self.vorschlaege_listbox.curselection():
            return

        # Ausgewähltes Molekül bekommen
        ausgewaehlter_name = self.vorschlaege_listbox.get(self.vorschlaege_listbox.curselection())

        # Molekül in der Hauptliste finden
        for i, molekuel in enumerate(self.molekuele):
            if molekuel["name"] == ausgewaehlter_name:
                # Zum gewählten Molekül wechseln
                self.aktueller_index = i
                self.zeige_aktuelles_molekuel()

                # Zum Üben-Modus wechseln
                self.wechsle_modus("Üben")

                # Suchfeld leeren und Vorschläge ausblenden
                self.such_var.set("")
                self.vorschlaege_listbox.delete(0, tk.END)
                break

    def waehle_gruppe(self):
        """Dialog zur Auswahl einer Molekülgruppe anzeigen"""
        gruppen_fenster = tk.Toplevel(self.root)
        gruppen_fenster.title("Molekülgruppe auswählen")
        gruppen_fenster.geometry("400x400")
        gruppen_fenster.transient(self.root)
        gruppen_fenster.grab_set()  # Modal machen

        tk.Label(gruppen_fenster, text="Welche Molekülgruppe möchtest du üben?",
                 font=("Arial", 12, "bold")).pack(pady=(20, 30))

        # Gruppe-Variable
        self.ausgewaehlte_gruppe = tk.StringVar()

        # Scrollbare Listbox für die Gruppen erstellen
        liste_frame = tk.Frame(gruppen_fenster)
        liste_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        scrollbar = tk.Scrollbar(liste_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        gruppen_listbox = tk.Listbox(liste_frame, width=30, height=10,
                                    yscrollcommand=scrollbar.set)
        gruppen_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=gruppen_listbox.yview)

        # Gruppen einfügen
        for gruppe in self.verfuegbare_gruppen:
            gruppen_listbox.insert(tk.END, gruppe)

        # Buttons
        button_frame = tk.Frame(gruppen_fenster)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Abbrechen",
                  command=gruppen_fenster.destroy).pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Auswählen",
                  command=lambda: [
                      self.ausgewaehlte_gruppe.set(gruppen_listbox.get(gruppen_listbox.curselection()[0])
                                    if gruppen_listbox.curselection() else ""),
                      gruppen_fenster.destroy(),
                      self.starte_gruppentraining()
                  ]).pack(side=tk.LEFT, padx=10)

        # Warten, bis das Fenster geschlossen wird
        self.root.wait_window(gruppen_fenster)

    def starte_gruppentraining(self):
        """Starte das Training für die ausgewählte Gruppe"""
        if not hasattr(self, 'ausgewaehlte_gruppe') or not self.ausgewaehlte_gruppe.get():
            self.wechsle_modus("Üben")
            return

        gruppe = self.ausgewaehlte_gruppe.get()

        # Moleküle der gewählten Gruppe finden
        self.gruppen_molekuele = [m for m in self.molekuele if m["gruppe"] == gruppe]

        if not self.gruppen_molekuele:
            messagebox.showinfo("Gruppentraining", f"Keine Moleküle in der Gruppe '{gruppe}' gefunden!")
            self.wechsle_modus("Üben")
            return

        # Zufällige Reihenfolge für das Training
        random.shuffle(self.gruppen_molekuele)

        # Erstes Molekül anzeigen
        self.aktueller_gruppen_index = 0
        self.zeige_gruppen_molekuel()

    def zeige_gruppen_molekuel(self):
        """Aktuelles Gruppenmolekül anzeigen"""
        if not hasattr(self, 'gruppen_molekuele') or not self.gruppen_molekuele:
            return

        molekuel = self.gruppen_molekuele[self.aktueller_gruppen_index]
        gruppe = molekuel["gruppe"]

        # Entsprechendes Molekül im Hauptarray finden
        for i, m in enumerate(self.molekuele):
            if m["nummer"] == molekuel["nummer"]:
                self.aktueller_index = i
                break

        # Molekül anzeigen
        self.zeige_aktuelles_molekuel()

        # Zusätzlich Gruppeninfo anzeigen
        gesamt = len(self.gruppen_molekuele)
        aktuell = self.aktueller_gruppen_index + 1

        self.name_label.config(text=f"{molekuel['name']}\n"
                                    f"Gruppe: {gruppe}\n"
                                    f"Molekül {aktuell} von {gesamt}")

    def erstelle_gruppenauswahl_panel(self):
        """Erstellt das Panel für die Gruppenauswahl im Gewertet-Modus in der Menüleiste"""
        # Falls das Panel bereits existiert, entfernen
        if hasattr(self, 'gruppen_auswahl_frame'):
            self.gruppen_auswahl_frame.destroy()

        # Beim ersten Aufruf die Checkbox-Variablen initialisieren
        if not hasattr(self, 'gruppen_checkboxes'):
            self.gruppen_checkboxes = {}
            for gruppe in self.verfuegbare_gruppen:
                self.gruppen_checkboxes[gruppe] = tk.BooleanVar(value=True)

        # Neues Panel erstellen - jetzt in der Menüleiste
        self.gruppen_auswahl_frame = tk.Frame(self.menu_frame, bg="#f0f0f0", bd=1)
        self.gruppen_auswahl_frame.pack(fill=tk.X, padx=5, pady=(10, 5))

        # Titel für Gruppenauswahl
        tk.Label(self.gruppen_auswahl_frame, text="Gruppen für Gewertet-Modus",
                 font=("Arial", 10, "bold"), bg="#f0f0f0").pack(pady=(5, 5))

        # Scrollbarer Bereich für Checkboxen
        checkbox_container = tk.Frame(self.gruppen_auswahl_frame, bg="#f0f0f0", height=180)
        checkbox_container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(checkbox_container, bg="#f0f0f0", highlightthickness=0, width=230, height=180)
        scrollbar = tk.Scrollbar(checkbox_container, orient=tk.VERTICAL, command=canvas.yview)

        checkbox_frame = tk.Frame(canvas, bg="#f0f0f0")
        checkbox_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=checkbox_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Checkboxen für jede Gruppe erstellen
        for gruppe in self.verfuegbare_gruppen:
            checkbox = tk.Checkbutton(checkbox_frame, text=gruppe,
                                      variable=self.gruppen_checkboxes[gruppe],
                                      bg="#f0f0f0", anchor=tk.W)
            checkbox.pack(fill=tk.X, pady=1)

        # Buttons für alle/keine auswählen
        button_frame = tk.Frame(self.gruppen_auswahl_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=5)

        tk.Button(button_frame, text="Alle", command=self.alle_gruppen_auswaehlen,
                  width=7).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Keine", command=self.keine_gruppen_auswaehlen,
                  width=7).pack(side=tk.RIGHT, padx=2)

    def aktualisiere_panel_zustand(self):
        """Aktualisiert die Anzeige des Panels basierend auf dem Ein-/Ausgeklappt-Zustand"""
        # Text und Symbol aktualisieren
        if self.panel_ausgeklappt.get():
            self.toggle_label.config(text="▼ Gruppen auswählen")

            # Alten Inhalt entfernen, falls vorhanden
            for widget in self.panel_inhalt.winfo_children():
                widget.destroy()

            # Panel-Inhalt anzeigen
            self.panel_inhalt.pack(fill=tk.BOTH, expand=True)

            # Scrollbarer Bereich für Checkboxen
            canvas = tk.Canvas(self.panel_inhalt, bg="#f5f5f5", width=180, height=300)
            scrollbar = tk.Scrollbar(self.panel_inhalt, orient=tk.VERTICAL, command=canvas.yview)

            checkbox_frame = tk.Frame(canvas, bg="#f5f5f5")
            checkbox_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

            canvas.create_window((0, 0), window=checkbox_frame, anchor=tk.NW)
            canvas.configure(yscrollcommand=scrollbar.set)

            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Checkboxen für jede Gruppe erstellen - mit bestehenden Variablen
            for gruppe in self.verfuegbare_gruppen:
                checkbox = tk.Checkbutton(checkbox_frame, text=gruppe,
                                          variable=self.gruppen_checkboxes[gruppe],
                                          bg="#f5f5f5", anchor=tk.W, padx=5)
                checkbox.pack(fill=tk.X, pady=2)

            # Buttons für alle/keine auswählen
            button_frame = tk.Frame(self.panel_inhalt, bg="#f5f5f5")
            button_frame.pack(fill=tk.X, pady=5, padx=5)

            tk.Button(button_frame, text="Alle", command=self.alle_gruppen_auswaehlen).pack(
                side=tk.LEFT, fill=tk.X, expand=True, padx=2)
            tk.Button(button_frame, text="Keine", command=self.keine_gruppen_auswaehlen).pack(
                side=tk.RIGHT, fill=tk.X, expand=True, padx=2)
        else:
            self.toggle_label.config(text="▶ Gruppen auswählen")
            # Panel-Inhalt entfernen wenn eingeklappt
            self.panel_inhalt.pack_forget()

    def alle_gruppen_auswaehlen(self):
        """Wählt alle Gruppen aus"""
        for var in self.gruppen_checkboxes.values():
            var.set(True)


    def keine_gruppen_auswaehlen(self):
        """Wählt keine Gruppen aus"""
        for var in self.gruppen_checkboxes.values():
            var.set(False)

if __name__ == "__main__":
    root = tk.Tk()
    app = MolekuelLernApp(root)
    root.mainloop()
