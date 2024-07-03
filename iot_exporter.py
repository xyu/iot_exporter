import argparse
import http.server
import logging
import socketserver

#
# Set up args
#

parser = argparse.ArgumentParser()
parser.add_argument(
	'-log',
	'--loglevel',
	default='warning',
	help='Provide logging level. Example --loglevel debug, default=warning'
)
args = parser.parse_args()

logging.basicConfig( level=args.loglevel.upper() )
logging.info( 'Logging now setup.' )

#
# App requirements
#

from iot_exporter import purpleair, util

_conf = util.get_conf()['DEFAULT']

#
# Run app
#

class ExporterHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
	def do_GET(self):
		match self.path:
			case '/metrics':
				self.send_response(200)
				self.send_header("Content-type", "text/plain")
				self.end_headers()

				output = []
				output += purpleair.collect()
				output.append("# EOF\n")

				self.wfile.write(bytes(
					"\n".join(output),
					"utf8"
				))
				return
			case _:
				self.send_response(404)
				self.send_header("Content-type", "text/plain")
				self.end_headers()

				self.wfile.write(bytes(
					"404 Not Found\n",
					"utf8"
				))
				return

# Create an object of the above class
_handler = ExporterHttpRequestHandler

# Create a server
_server = socketserver.TCPServer(
	(_conf.get('server_host'), int(_conf.get('server_port'))),
	_handler
)

# Start the server
try:
	_server.serve_forever()
except KeyboardInterrupt:
	print('^C received, shutting down server')
	_server.socket.close()
