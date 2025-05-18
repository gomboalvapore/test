# Importa la classe Flask, le funzioni request, jsonify e send_from_directory dal modulo flask
from flask import Flask, request, jsonify, send_from_directory
# Importa os per gestire i percorsi dei file
import os
# Importa SQLAlchemy dal modulo flask_sqlalchemy
from flask_sqlalchemy import SQLAlchemy

# Crea un'istanza dell'applicazione Flask
app = Flask(__name__, static_folder='.') # Il punto '.' indica la directory corrente

# --- Configurazione del Database ---
# Definisci l'URI del database. Per SQLite, è 'sqlite:///nome_file.db'
# __file__ è il percorso dello script corrente, os.path.abspath lo rende assoluto
# os.path.dirname ottiene la directory dello script
# os.path.join costruisce il percorso completo al file del database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(os.path.abspath(__file__)), 'site.db')
# Disabilita il tracciamento delle modifiche, che non è necessario per questo esempio e consuma risorse
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Crea un'istanza di SQLAlchemy, passandole l'applicazione Flask
db = SQLAlchemy(app)

# --- Definizione del Modello del Database ---
# Definisci una classe Python che rappresenta la tabella nel database
class Number(db.Model):
    # Definisci il nome della tabella nel database
    __tablename__ = 'number_storage'
    # Definisci le colonne della tabella
    # 'id' è la chiave primaria, autoincrementante
    id = db.Column(db.Integer, primary_key=True)
    # 'value' è la colonna dove memorizzeremo il numero, è un intero e non può essere nullo
    value = db.Column(db.Integer, nullable=False, default=0) # Imposta un valore di default a 0

    # Metodo per rappresentare l'oggetto in modo leggibile (opzionale)
    def __repr__(self):
        return f'<Number {self.value}>'

# --- Route e Logica dell'Applicazione ---

# Definisci la route per la homepage (pagina di modifica)
@app.route('/')
def index():
    # Questa route serve il file index.html dalla directory corrente
    return send_from_directory('.', 'index.html')

# Definisci la route per la pagina di sola visualizzazione
@app.route('/view')
def view_only():
    # Questa route serve il file view_only.html dalla directory corrente
    return send_from_directory('.', 'view_only.html')

# Definisci la route per ottenere il numero (usata da entrambe le pagine)
@app.route('/get_number', methods=['GET'])
def get_number():
    # Cerca il primo (e unico, in questo caso) record nella tabella Number
    # Se non esiste, crea un nuovo record con il valore di default (0)
    current_number_obj = Number.query.first()
    if not current_number_obj:
        # Se la tabella è vuota, crea un nuovo oggetto Number
        new_number_obj = Number(value=0) # Crea un nuovo record con valore 0
        db.session.add(new_number_obj) # Aggiungi il nuovo record alla sessione del database
        db.session.commit() # Salva le modifiche nel database
        current_number = 0 # Il numero corrente è 0
    else:
        # Se il record esiste, prendi il suo valore
        current_number = current_number_obj.value

    # Restituisce il numero come risposta JSON
    return jsonify({'number': current_number})

# Definisci la route per impostare il numero (usata solo dalla pagina di modifica)
@app.route('/set_number', methods=['POST'])
def set_number():
    # Ottiene i dati JSON inviati dal frontend
    data = request.get_json()
    # Estrae il numero dai dati JSON
    new_number_value = data.get('number')

    # Controlla se il valore è un numero valido
    if new_number_value is not None and isinstance(new_number_value, int):
        # Cerca il primo (e unico) record del numero
        number_obj = Number.query.first()

        if number_obj:
            # Se il record esiste, aggiorna il suo valore
            number_obj.value = new_number_value
        else:
            # Se il record non esiste (non dovrebbe succedere dopo la prima get, ma per sicurezza)
            # Crea un nuovo record
            number_obj = Number(value=new_number_value)
            db.session.add(number_obj) # Aggiungi il nuovo record alla sessione

        # Salva le modifiche nel database
        db.session.commit()

        # Restituisce un messaggio di successo come risposta JSON
        return jsonify({'message': 'Numero aggiornato con successo nel database!'}), 200
    else:
        # Se il numero non è valido, restituisce un messaggio di errore
        return jsonify({'error': 'Dati non validi. Si aspettava un numero intero.'}), 400

# Esegui l'applicazione Flask se lo script viene eseguito direttamente
if __name__ == '__main__':
    # --- Creazione del Database e della Tabella ---
    # Questo blocco viene eseguito solo quando lo script viene avviato direttamente
    # Crea il database e le tabelle definite nei modelli, se non esistono già
    with app.app_context(): # Necessario per usare le funzionalità di Flask-SQLAlchemy fuori dalle richieste
        db.create_all()
        # Inizializza il numero se la tabella è vuota
        if not Number.query.first():
            initial_number = Number(value=0)
            db.session.add(initial_number)
            db.session.commit()

    # Avvia il server Flask in modalità debug
    app.run(debug=True)
