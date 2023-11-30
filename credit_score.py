import logging
import sys
from spyne import Application, rpc, ServiceBase, Integer, Unicode, Double
from spyne .protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.util.wsgi_wrapper import run_twisted
import json

logging.basicConfig(level=logging.DEBUG)


class CreditScoreService(ServiceBase):
    @rpc(Unicode, Unicode, Integer, Integer, _returns=Double)
    def credit_scoring(ctx, credits, finances, duree_emprunt, valeur_empreint):

        credits = json.loads(credits)["credits"]
        finances = json.loads(finances)["finances"]

        print(credits)
        print(finances)
        print("duree_emprunt:", duree_emprunt)
        print("valeur_empreint:", valeur_empreint)
        montant_a_payer_mois = 0
        revenus = 0
        depenses = 0
        solde = 0
        montant_credit_deja_paye = 0

        for i in range(len(credits)):
            if credits[i]["etat"] == "Retard":
                return 0
            else:
                if credits[i]["etat"] == "en cours":
                    montant_a_payer_mois += credits[i]["montant_init"]\
                        / credits[i]["duree"]
                else:
                    montant_credit_deja_paye += credits[i]["montant_init"]\
                        / credits[i]["duree"]
        for i in range(len(finances)):
            revenus += finances[i]["revenus"]
            depenses += finances[i]["depenses"]
            solde += finances[i]["solde"]
        capacite_achat = revenus - depenses
        score = capacite_achat - montant_a_payer_mois + solde\
            / duree_emprunt - (valeur_empreint/duree_emprunt)
        print(score)
        return score


application = Application([CreditScoreService], tns='spyne.exemples.\
                          credit_score',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())

if __name__ == '__main__':
    wsgi_app = WsgiApplication(application)
    twisted_apps = [
        (wsgi_app, b'CreditScoreService'),
    ]
sys.exit(run_twisted(twisted_apps, 8100))
