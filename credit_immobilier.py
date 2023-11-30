import logging
import sys
from spyne import Application, rpc, ServiceBase, Unicode
from spyne .protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.util.wsgi_wrapper import run_twisted
from suds.client import Client
import pandas as pd
import json
import mysql.connector

logging.basicConfig(level=logging.DEBUG)


class CreditImmobilierService(ServiceBase):
    @rpc(Unicode, _returns=Unicode)
    def credit_immobilier(ctx, data):
        json_data = json.loads(data)

        # Extract the "data" part from the dictionary
        data = json_data["data"]
        columns = json_data["columns"]
        # Create a Pandas DataFrame
        data_client = pd.DataFrame(data, columns=columns)

        dbmanage = DbManager()
        etl = ETL()
        nom_client = data_client["Nom_du_Client"][0]
        adresse_mail = data_client["Email"][0]
        duree_pret = data_client["Duree_du_Pret"][0]
        montant_pret = data_client["Montant_du_Pret_Demande"][0]
        adresse_appart = data_client["Adresse"][0]
        num_bat = data_client["Num_bat"][0]
        num_appart = data_client["Num_appart"][0]

        credits = etl.extract_credit(dbmanage.get_credit_client(nom_client))
        finances = etl.extract_finances(dbmanage.
                                        get_finance_client(nom_client))

        credits_json_list = json.dumps({"credits": credits})
        finances_json_list = json.dumps({"finances": finances})

        client_credit_score = Client('http://localhost:8100\
                                     /CreditScoreService?wsdl', cache=None)
        credit_score = client_credit_score.service.credit_scoring(
            credits_json_list, finances_json_list, duree_pret, montant_pret)

        client_solvabilite = Client('http://localhost:8200\
                                    /SolvabiliteService?wsdl', cache=None)
        solvabilite = client_solvabilite.service.solvabilite(credit_score,
                                                             revenus=3000,
                                                             depenses=1700)
        if solvabilite:
            client_appart = Client('http://localhost:8300\
                                   /AppartementService?wsdl', cache=None)
            appart = client_appart.service.verif_appart(adresse_appart,
                                                        num_bat, num_appart)
            appart_prix = json.loads(appart)["Prix"]
            appart_conforme = json.loads(appart)["Conforme"]
        else:
            appart_prix = 0.0
            appart_conforme = False
        client_decision = Client('http://localhost:8400\
                                 /DecisonService?wsdl',
                                 cache=None)
        decision = client_decision.service.decision(adresse_mail, montant_pret,
                                                    solvabilite,
                                                    appart_prix,
                                                    appart_conforme)

        return decision


class DbManager:
    def __init__(self):
        config = {
            'user': 'root',
            'password': '171969',
            'host': 'localhost',
            'port': 3306,
            'database': 'mydb'
        }

        # Établissez la connexion à la base de données
        self.conn = mysql.connector.connect(**config)
        print("*****************************************************")
        # Créez un objet curseur pour exécuter des requêtes SQL
        self.cursor = self.conn.cursor()

    def get_credit_client(self, name):
        # Exécutez la requête SELECT
        query = "SELECT * FROM credit, client where client.Id_client = credit.\
            Id_client and client.Nom = '"+name+"'"
        self.cursor.execute(query)

        # Récupérez les résultats de la requête
        result = self.cursor.fetchall()

        return result

    def get_finance_client(self, name):
        query = "select * from compte as C , client as A where C.Id_client=A.\
            Id_client and A.Nom = '"+name+"'"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result

    def close_connection(self):
        self.cursor.close()
        self.conn.close()


class ETL:
    def extract_credit(self, credits):
        result = []
        for credit in credits:
            result.append({"montant_init": credit[1],
                           "duree": credit[3],
                           "etat": credit[5]})
        return result

    def extract_finances(self, finances):
        result = []
        for finance in finances:
            result.append({"revenus": finance[2],
                           "depenses": finance[1],
                           "solde": finance[3]})
        return result


application = Application([CreditImmobilierService], tns='spyne.exemples.\
                          credit_immobilier',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())

if __name__ == '__main__':
    wsgi_app = WsgiApplication(application)
    twisted_apps = [
        (wsgi_app, b'CreditImmobilierService'),
    ]
sys.exit(run_twisted(twisted_apps, 8090))
