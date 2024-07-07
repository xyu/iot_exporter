import logging
import math
import requests
import time

from iot_exporter import util

_logger = logging.getLogger(__name__)
_conf = util.get_conf()['beestat']
_cache = {}
_cache_count = {
	'hit': 0,
	'miss': 0,
}
_session = requests.Session()
_session.headers.update({
	'Cookie': f"session_key={_conf.get('session_key')}"
})

#
# Configure Exported Metrics
#

METRICS = {

	'ecobee_temperature_fahrenheit': {
		'HELP': 'Temperature reported by ecobee sensor.',
		'TYPE': 'gauge',
		'UNIT': 'fahrenheit',
		'capability_type': 'temperature',
		'normalize': lambda x : int(x) / 10,
	},

	'ecobee_humidity_ratio': {
		'HELP': 'Relative humidity reported by ecobee sensor.',
		'TYPE': 'gauge',
		'UNIT': 'ratio',
		'capability_type': 'humidity',
		'normalize': lambda x : int(x) / 100,
	},

}

#
# Helper Functions
#

def get_metric(metric: str, data: dict) -> list:
	outputs = []

	if not data['success'] or 'data' not in data:
		_logger.debug("API data from beestat.io is not valid")
		return output

	for sensor_data in data['data'].values():
		if not sensor_data['in_use']:
			_logger.debug("Skipping not in use sensor data")
			continue

		output = {
			'labels': {
				'thermostat_id': sensor_data.get('ecobee_thermostat_id'),
				'sensor_id': sensor_data.get('ecobee_sensor_id'),
				'name': sensor_data.get('name'),
			},
			'value': None,
		}

		for capability in sensor_data.get('capability'):
			if capability.get('type') == METRICS[metric]['capability_type']:
				output['value'] = METRICS[metric]['normalize'](capability.get('value'))
				break

		outputs.append(output)

	return outputs

def query_api() -> dict:
	global _cache
	global _cache_count

	if 'timestamp' not in _cache:
		_cache = {
			'timestamp': 0,
			'data': {},
		}

	if time.time() - _cache['timestamp'] < int(_conf.get('api_cache_time')):
		_cache_count['hit'] += 1
		return _cache['data']
	else:
		_cache['timestamp'] = time.time() # stampede protection

	_cache_count['miss'] += 1
	response = _session.get(
		_conf.get('api_endpoint'),
		params = {
			'api_key': _conf.get('api_key'),
			'resource': 'ecobee_sensor',
			'method': 'read_id',
		}
	)

	if response.status_code == 200:
		_cache['data'] = response.json()
		_cache['data']['_timestamp'] = time.time()

	return _cache['data']

def collect() -> list:
	global _cache_count

	data = query_api()

	output = []

	# Metric fields
	for metric_name, metric_def in METRICS.items():
		for desc in [ 'TYPE', 'UNIT', 'HELP' ]:
			if desc in metric_def:
				output.append("# %s %s %s" % (
					desc,
					metric_name,
					metric_def[desc]
				))

		for metric in get_metric(metric_name, data):
			if metric['value'] is None:
				_logger.debug("Did not find a value for: %s", metric_name)
				continue

			output.append("%s{%s} %f %i" % (
				metric_name,
				util.to_label_param(metric['labels']),
				metric['value'],
				data['_timestamp'] * 1000
			))

		output.append('')

	# Meta stats fields
	meta = 'ecobee_api_requests_total'
	output.append("# TYPE %s counter" % (meta))
	output.append("# HELP %s Count of API requests made and skipped due to existing cache" % (meta))
	output.append('%s{cache="%s"} %f' % (
		meta,
		'hit',
		_cache_count['hit']
	))
	output.append('%s{cache="%s"} %f' % (
		meta,
		'miss',
		_cache_count['miss']
	))
	output.append('')

	return output
