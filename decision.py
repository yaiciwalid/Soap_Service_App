import logging
import sys
from spyne import Application, rpc, ServiceBase, Unicode, Double, Boolean
from spyne .protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.util.wsgi_wrapper import run_twisted
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logging.basicConfig(level=logging.DEBUG)


class DecisonService(ServiceBase):
    @rpc(Unicode, Double, Boolean, Double, Boolean, _returns=Unicode)
    def decision(ctx, adresse_mail, montant_pret, solvabilite, prix_appart,
                 conformite_appart):
        decis = "Refus"
        if solvabilite and conformite_appart:
            if montant_pret <= prix_appart:
                message = "Nous avons le plaisir de vous annoncer que votre \
                    pret a ete accepté."
                decis = "accepte"
            else:
                message = "Votre pret a été réevalué a " + str(prix_appart)
                decis = "reevalue"
        else:
            message = "Nous sommes au regret de vous annoncer que votre pret a\
                 été refusé"

        # Informations du compte d'expédition
        expediteur_email = ""
        expediteur_mot_de_passe = ""

        # Création du message
        objet = "Test Soap"

        msg = MIMEMultipart()
        msg['From'] = expediteur_email
        msg['To'] = adresse_mail
        msg['Subject'] = objet
        msg.attach(MIMEText(message, 'plain'))

        # Connexion au serveur SMTP de Gmail (dans cet exemple)
        serveur_smtp = smtplib.SMTP('smtp.gmail.com', 587)
        serveur_smtp.starttls()
        serveur_smtp.login(expediteur_email, expediteur_mot_de_passe)

        # Envoi de l'e-mail
        serveur_smtp.sendmail(expediteur_email, adresse_mail, msg.as_string())

        # Fermeture de la connexion
        serveur_smtp.quit()
        return decis


application = Application([DecisonService], tns='spyne.exemples.decision',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())

if __name__ == '__main__':
    wsgi_app = WsgiApplication(application)
    twisted_apps = [
        (wsgi_app, b'DecisonService'),
    ]
sys.exit(run_twisted(twisted_apps, 8400))
