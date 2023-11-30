import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from suds.client import Client
import os


# Créez une classe d'événement pour gérer les changements de fichiers
class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        # Nouveau fichier créé
        print(f'Nouveau fichier créé : {event.src_path}')
        # Utilisez la fonction os.path.basename pour obtenir le nom du fichier
        nom_fichier = os.path.basename(event.src_path)

        print(nom_fichier)
        client_extract = Client('http://localhost:8080/ExctractService?wsdl', 
                                cache=None)
        extracted_data = client_extract.service.exctract_data_from_file(
            nom_fichier)
        print(extracted_data)
        client_credit_immo = Client('http://localhost:8090/\
                                    CreditImmobilierService?wsdl',
                                    cache=None)
        credit_immo_data = client_credit_immo.service.credit_immobilier(
            extracted_data)
        return credit_immo_data


# Spécifiez le dossier à surveiller
folder_to_watch = 'C:/Users/hw_ya/Desktop/uvsq/SOA/DossierDepot'

if __name__ == "__main__":
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=folder_to_watch, recursive=False)

    # Démarrez l'observateur
    observer.start()
    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()

    observer.join()
