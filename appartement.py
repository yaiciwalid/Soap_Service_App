import logging
import sys
from spyne import Application, rpc, ServiceBase, Integer, Unicode
from spyne .protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.util.wsgi_wrapper import run_twisted
import json
import pymongo
logging.basicConfig(level=logging.DEBUG)


class AppartementService(ServiceBase):
    @rpc(Unicode, Integer, Integer, _returns=Unicode)
    def verif_appart(ctx, adresse, num_bat, num_appart):
        dbmanager = DbManage()
        print(dbmanager.get_info_appart(adresse, num_bat, num_appart))
        return json.dumps(dbmanager.get_info_appart(adresse, num_bat,
                                                    num_appart))


class DbManage:
    def __init__(self):
        # Établir une connexion à MongoDB
        # Remplacez l'URL de connexion par celle de votre base de données
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        # Remplacez "ma_base_de_donnees" par le nom de votre base de données
        db = client.Appartements
        # Remplacez "ma_collection" par le nom de votre collection
        self.collection = db.Appart

    def get_info_appart(self, adresse, num_bat, num_appart):
        query = {"Num_bat": num_bat,    "Num_appart": num_appart,
                 "Adresse": adresse}
        results = self.collection.find(query)
        res = results.next()
        return {"Conforme": res["Conforme"],
                "Prix": res["prix"]}


application = Application([AppartementService],
                          tns='spyne.exemples.verif_appart',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())

if __name__ == '__main__':
    wsgi_app = WsgiApplication(application)
    twisted_apps = [
        (wsgi_app, b'AppartementService'),
    ]
sys.exit(run_twisted(twisted_apps, 8300))
