import logging
import sys
from spyne import Application, rpc, ServiceBase, Double, Boolean
from spyne .protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.util.wsgi_wrapper import run_twisted

logging.basicConfig(level=logging.DEBUG)


class SolvabiliteService(ServiceBase):
    @rpc(Double, Double, Double, _returns=Boolean)
    def solvabilite(ctx, credit_score, revenus, depenses):
        if credit_score > 500 and revenus > depenses:
            return True
        else:
            return False


application = Application([SolvabiliteService], tns='spyne.exemples.\
                          solvabilite',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())

if __name__ == '__main__':
    wsgi_app = WsgiApplication(application)
    twisted_apps = [
        (wsgi_app, b'SolvabiliteService'),
    ]
sys.exit(run_twisted(twisted_apps, 8200))
