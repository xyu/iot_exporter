import logging
import math
import requests
import time

from iot_exporter import util

_logger = logging.getLogger(__name__)
_conf = util.get_conf()['openweather']
_lat_lon = None
_cache = {}
_cache_count = {
	'hit': 0,
	'miss': 0,
}
_session = requests.Session()

METRICS = {

	'openweather_temperature_fahrenheit': {
		'HELP': 'Current temperature.',
		'TYPE': 'gauge',
		'UNIT': 'fahrenheit',
		'fields': {
			'main.temp': {'type': 'real'},
			'main.temp_min': {'type': 'real_min'},
			'main.temp_max': {'type': 'real_max'},
			'main.feels_like': {'type': 'feel'},
		},
		# Defaults to Kelvin
		'normalize': lambda field, x : ( x - 273.15 ) * 1.8 + 32,
	},

	'openweather_humidity_ratio': {
		'HELP': 'Relative humidity.',
		'TYPE': 'gauge',
		'UNIT': 'ratio',
		'fields': {
			'main.humidity': {},
		},
		'normalize': lambda field, x : x / 100,
	},

	'openweather_pressure_millibars': {
		'HELP': 'Atmospheric pressure on the sea level.',
		'TYPE': 'gauge',
		'UNIT': 'millibars',
		'fields': {
			'main.pressure': {},
		},
	},

	'openweather_visual_range_meters': {
		'HELP': 'Often referred to as visibility, capped at 10km.',
		'TYPE': 'gauge',
		'UNIT': 'meters',
		'fields': {
			'visibility': {},
		},
	},

	'openweather_wind_meters_per_second': {
		'HELP': 'Wind speed.',
		'TYPE': 'gauge',
		'UNIT': 'meters_per_second',
		'fields': {
			'wind.speed': {'type': 'speed'},
			'wind.gust': {'type': 'gust'},
		},
	},

	'openweather_cloud_ratio': {
		'HELP': 'Cloudiness.',
		'TYPE': 'gauge',
		'UNIT': 'ratio',
		'fields': {
			'clouds.all': {},
		},
		'normalize': lambda field, x : x / 100,
	},

}

def get_lat_lon() -> dict:
	global _lat_lon

	if _lat_lon:
		return _lat_lon

	response = _session.get(
		_conf.get('geo_endpoint'),
		params = {
			'zip': _conf.get('zip'),
			'appid': _conf.get('api_key'),
		}
	)

	if response.status_code != 200:
		raise RuntimeError(f'Could not geo locate the zip code {_conf.get('zip')}')

	_lat_lon = response.json()
	return _lat_lon

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

	lat_lon = get_lat_lon()

	_cache_count['miss'] += 1
	response = _session.get(
		_conf.get('api_endpoint'),
		params = {
			'lat': lat_lon['lat'],
			'lon': lat_lon['lon'],
			'appid': _conf.get('api_key'),
		}
	)

	if response.status_code == 200:
		_cache['data'] = response.json()

	return _cache['data']

def get_value(data: dict, key: str):
	key_parts = key.split('.')
	data_part = data
	for key_part in key_parts:
		if key_part not in data_part:
			return None
		data_part = data_part[key_part]
	return data_part

def collect() -> list:
	global _cache_count

	data = query_api()
	lat_lon = get_lat_lon()

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

		for field_name, labels in metric_def['fields'].items():
			value = get_value(data, field_name)
			if value is None:
				_logger.debug("Did not find a value for: %s", field_name)
				continue

			# Add in location info
			labels['name'] = lat_lon['name']
			labels['zip'] = lat_lon['zip']

			# See if we need to normalize the value
			if 'normalize' in metric_def:
				value = metric_def['normalize'](
					field_name,
					value
				)

			output.append("%s{%s} %f %i" % (
				metric_name,
				util.to_label_param(labels),
				value,
				data['dt'] * 1000
			))

		output.append('')

	# Meta stats fields
	meta = 'openweather_api_requests_total'
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