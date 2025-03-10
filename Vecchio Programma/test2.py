import pymssql

# Parametri di connessione al database
server = "192.168.7.226\sqlexpress"
database = "ScambioVisione"
username = "visione"
password = "Visione123!"

# Connessione al database
conn = pymssql.connect(server=server, user=username, password=password, database=database)
cursor = conn.cursor()

# Query di aggiornamento
query = "UPDATE tblScambioVisione SET Bilancelle = 4 WHERE IduScambioVisione = 10"

try:
    # Esecuzione della query
    cursor.execute(query)
    
    # Commit delle modifiche
    conn.commit()
    print("Modifica effettuata con successo!")

except Exception as e:
    # Gestione dell'errore in caso di fallimento
    print(f"Errore durante l'esecuzione della query: {e}")
    conn.rollback()

finally:
    # Chiusura della connessione al database
    conn.close()


"""
# Supponendo che le tue variabili siano nuovi_valore_bilancelle e nuovi_valore_ganci
nuovi_valori_bilancelle = 123  # Sostituisci con il valore effettivo per Bilancelle
nuovi_valori_ganci = 789  # Sostituisci con il valore effettivo per Ganci (deve essere un valore intero)

# Costruisci la query con le variabili
query = "UPDATE tblScambioVisione SET Bilancelle = %s, Ganci = %d WHERE IduScambioVisione = 10"

# Esegui la query passando le variabili come argomenti
cursor.execute(query, (nuovi_valori_bilancelle, nuovi_valori_ganci))

"""