
from nintendo.nex.nat import NATTraversalServer
from nintendo.nex.notification import NotificationServer
from nintendo.nex.nintendo_notification import NintendoNotificationServer
from nintendo.nex.authentication import AuthenticationClient
from nintendo.nex.secure import SecureClient
from nintendo.nex.friends import FriendsTitle
from nintendo.nex.common import NexEncoder


class NintendoLoginData(NexEncoder):
	def init(self, token):
		self.token = token
		
	def get_name(self):
		return "NintendoLoginData"
		
	def encode_old(self, stream):
		stream.string(self.token)


class BackEndClient:
	def __init__(self, access_key, version):
		self.access_key = access_key.encode("ascii")
		self.version = version
		
		self.auth_client = None
		self.secure_client = None
		
		self.nat_traversal_server = NATTraversalServer()
		self.notification_server = NotificationServer()
		self.nintendo_notification_server = NintendoNotificationServer()

		self.protocol_map = {
			NATTraversalServer.PROTOCOL_ID: self.nat_traversal_server,
			NotificationServer.PROTOCOL_ID: self.notification_server,
			NintendoNotificationServer.PROTOCOL_ID: self.nintendo_notification_server
		}
		
	def connect(self, host, port):
		self.auth_client = AuthenticationClient(self, self.access_key)
		self.auth_client.connect(host, port)
		
	def close(self):
		self.auth_client.close()
		if self.secure_client:
			self.secure_client.close()
		
	def login(self, username, password, token=None):
		if token and self.version != FriendsTitle.NEX_VERSION:
			self.auth_client.login_ex(username, password, token)
		else:
			self.auth_client.login(username, password)

		ticket = self.auth_client.request_ticket()
		host = self.auth_client.secure_station["address"]
		port = self.auth_client.secure_station["port"]
		
		self.secure_client = SecureClient(self, self.access_key, ticket, self.auth_client)
		self.secure_client.connect(host, port)
		if self.version == FriendsTitle.NEX_VERSION:
			urls = self.secure_client.register_urls(NintendoLoginData(token))
		else:
			urls = self.secure_client.register_urls()
		self.local_station, self.public_station = urls
		
	def login_guest(self):
		self.login("guest", "MMQea3n!fsik")
