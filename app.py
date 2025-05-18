# Importa la classe Flask, le funzioni request, jsonify e send_from_directory dal modulo flask
from flask import Flask, request, jsonify, send_from_directory
# Importa os per gestire i percorsi dei file
import os

# Crea un'istanza dell'applicazione Flask
# Specifichiamo la cartella root dove si trova l'applicazione
app = Flask(__name__, static_folder='.') # Il punto '.' indica la directory corrente

# Definisci il nome del file dove memorizzare il numero
NUMBER_FILE = 'number.txt'

# Funzione per leggere il numero dal file
def read_number():
    # Controlla se il file esiste
    if os.path.exists(NUMBER_FILE):
        try:
            # Apri il file in modalità lettura ('r')
            with open(NUMBER_FILE, 'r') as f:
                # Leggi la prima riga (che dovrebbe contenere il numero)
                content = f.read().strip()
                # Prova a convertire il contenuto in un numero intero
                return int(content) if content else 0 # Restituisce 0 se il file è vuoto
        except ValueError:
            # Se la conversione fallisce, significa che il file contiene qualcosa di non numerico
            print(f"Attenzione: Il file {NUMBER_FILE} contiene un valore non numerico. Verrà usato 0.")
            return 0
        except Exception as e:
            # Gestisce altri possibili errori di lettura
            print(f"Errore nella lettura del file {NUMBER_FILE}: {e}")
            return 0
    else:
        # Se il file non esiste, restituisce 0 come valore iniziale
        return 0

# Funzione per scrivere il numero nel file
def write_number(number):
    try:
        # Apri il file in modalità scrittura ('w'). Se il file esiste, viene sovrascritto.
        with open(NUMBER_FILE, 'w') as f:
            # Scrivi il numero (convertito in stringa) nel file
            f.write(str(number))
    except Exception as e:
        # Gestisce possibili errori di scrittura
        print(f"Errore nella scrittura del file {NUMBER_FILE}: {e}")

# Definisci la route per la homepage (pagina di modifica)
@app.route('/')
def index():
    # Questa route serve il file index.html dalla directory corrente
    return send_from_directory('.', 'index.html') # Il primo '.' indica la directory corrente

# Definisci la NUOVA route per la pagina di sola visualizzazione
@app.route('/view')
def view_only():
    # Questa route serve il file view_only.html dalla directory corrente
    return send_from_directory('.', 'view_only.html')

# Definisci la route per ottenere il numero (usata da entrambe le pagine)
@app.route('/get_number', methods=['GET'])
def get_number():
    # Legge il numero dal file
    current_number = read_number()
    # Restituisce il numero come risposta JSON
    return jsonify({'number': current_number})

# Definisci la route per impostare il numero (usata solo dalla pagina di modifica)
@app.route('/set_number', methods=['POST'])
def set_number():
    # Ottiene i dati JSON inviati dal frontend
    data = request.get_json()
    # Estrae il numero dai dati JSON
    new_number = data.get('number')

    # Controlla se il numero è stato ricevuto e se è un numero intero
    if new_number is not None and isinstance(new_number, int):
        # Scrive il nuovo numero nel file
        write_number(new_number)
        # Restituisce un messaggio di successo come risposta JSON
        return jsonify({'message': 'Numero aggiornato con successo!'}), 200
    else:
        # Se il numero non è valido, restituisce un messaggio di errore
        return jsonify({'error': 'Dati non validi. Si aspettava un numero intero.'}), 400

# Esegui l'applicazione Flask se lo script viene eseguito direttamente
if __name__ == '__main__':
    # Crea il file number.txt se non esiste e scrivici 0 come valore iniziale
    if not os.path.exists(NUMBER_FILE):
        write_number(0)
    # Avvia il server Flask in modalità debug (utile per lo sviluppo)
    # host='0.0.0.0' rende il server accessibile esternamente (se necessario)
    # port=5000 è la porta di default di Flask
    app.run(debug=True)
