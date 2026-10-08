from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

authorizer = DummyAuthorizer()
authorizer.add_user("svc_backup", "B4ckup_Serv1ce_2024", "/home/svc_backup", perm="elr")

handler = FTPHandler
handler.authorizer = authorizer
handler.banner = "CeylonGov Secure - Internal Backup Service"

handler.passive_ports = range(2121, 2131)

server = FTPServer(("0.0.0.0", 21), handler)
server.serve_forever()
