import logging
import sys
from spyne import Application, rpc, ServiceBase, Unicode
from spyne .protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from spyne.util.wsgi_wrapper import run_twisted
import pandas as pd

logging.basicConfig(level=logging.DEBUG)


class ExctractService(ServiceBase):
    @rpc(Unicode, _returns=Unicode)
    def exctract_data_from_file(ctx, file_path):
        df = pd.read_csv("DossierDepot/"+file_path, delimiter=';', header=0)
        print(df)
        df_json = df.to_json(orient='split')
        return df_json


application = Application([ExctractService], tns='spyne.exemples.hello',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())

if __name__ == '__main__':
    wsgi_app = WsgiApplication(application)
    twisted_apps = [
        (wsgi_app, b'ExctractService'),
    ]
sys.exit(run_twisted(twisted_apps, 8080))
