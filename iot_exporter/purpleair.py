import logging
import requests
import time

from iot_exporter import util

_logger = logging.getLogger(__name__)
_conf = util.get_conf()['purpleair']
_cache = {}
_session = requests.Session()
_session.headers.update({'X-API-Key': _conf.get('api_key')})

#
# Configure Exported Metrics
#

INFO_FIELDS = {

	'purpleair_device_info': [
		'name',
		'model',
		'hardware',
		'firmware_version',
	],

	'purpleair_location_info': [
		'location_type',
		'longitude',
		'latitude',
		'altitude',
	],

}

METRICS = {

	'purpleair_confidence_ratio': {
		'HELP': 'The average of confidence_manual and confidence_auto indicating how closely channel A and B pseudo averages match each other.',
		'TYPE': 'gauge',
		'UNIT': 'ratio',
		'fields': {
			'confidence': {},
		},
		'normalize': lambda field, x : x / 100,
	},

	'purpleair_humidity_ratio': {
		'HELP': 'Relative humidity inside of the sensor housing.',
		'TYPE': 'gauge',
		'UNIT': 'ratio',
		'fields': {
			'humidity_a': {'channel': 'A'},
			'humidity_b': {'channel': 'B'},
		},
		# Raw value is on average is 4% lower than ambient conditions
		'normalize': lambda field, x : min(1, x / 100 + 0.04),
	},

	'purpleair_temperature_fahrenheit': {
		'HELP': 'Relative humidity inside of the sensor housing.',
		'TYPE': 'gauge',
		'UNIT': 'fahrenheit',
		'fields': {
			'temperature_a': {'channel': 'A'},
			'temperature_b': {'channel': 'B'},
		},
		# Raw value is on average is 8°F higher than ambient conditions.
		'normalize': lambda field, x : x - 8,
	},

	'purpleair_pressure_millibars': {
		'HELP': 'Current pressure in Millibars.',
		'TYPE': 'gauge',
		'UNIT': 'millibars',
		'fields': {
			'pressure_a': {'channel': 'A'},
			'pressure_b': {'channel': 'B'},
		},
	},

	'purpleair_voc': {
		'HELP': 'VOC concentration (IAQ) in Bosch static iaq units as per BME680 spec sheet, EXPERIMENTAL.',
		'TYPE': 'gauge',
		'fields': {
			'voc_a': {'channel': 'A'},
			'voc_b': {'channel': 'B'},
		},
	},

	'purpleair_pm_aqi': {
		'HELP': 'US EPA AQI based on PM2.5 / PM10 particulate concentrations',
		'TYPE': 'gauge',
		'fields': {
			'pm2.5_alt_a': {'channel': 'A', 'pm': '2.5'},
			'pm2.5_alt_b': {'channel': 'B', 'pm': '2.5'},
			'pm10.0_a': {'channel': 'A', 'pm': '10.0'},
			'pm10.0_b': {'channel': 'B', 'pm': '10.0'},
		},
		'normalize': lambda field, x : calc_epa_aqi( field, x ),
	},

	'purpleair_pm_concentration_ug_per_m3': {
		'HELP': 'Estimated mass concentration (µg/m³) of PM1 / PM2.5 / PM10 particulates with a diameter of fewer than 1 / 2.5 / 10 microns.',
		'TYPE': 'gauge',
		'UNIT': 'ug_per_m3',
		'fields': {
			'pm1.0_a': {'channel': 'A', 'pm': '1.0'},
			'pm1.0_b': {'channel': 'B', 'pm': '1.0'},
			'pm2.5_alt_a': {'channel': 'A', 'pm': '2.5'},
			'pm2.5_alt_b': {'channel': 'B', 'pm': '2.5'},
			'pm10.0_a': {'channel': 'A', 'pm': '10.0'},
			'pm10.0_b': {'channel': 'B', 'pm': '10.0'},
		},
	},

	'purpleair_visual_range_meters': {
		'HELP': 'Often referred to as visibility, visual range is the distance from the observer that a large dark object, e.g. a mountain top or large building, just disappears from view.',
		'TYPE': 'gauge',
		'UNIT': 'meters',
		'fields': {
			'visual_range_a': {'channel': 'A'},
			'visual_range_b': {'channel': 'B'},
		},
		'normalize': lambda field, x : x * 1000,
	},

	'purpleair_light_scattering_deciviews': {
		'HELP': 'A haze index related to light scattering and extinction that is approximately linearly related to human perception of the haze.',
		'TYPE': 'gauge',
		'UNIT': 'deciviews',
		'fields': {
			'deciviews_a': {'channel': 'A'},
			'deciviews_b': {'channel': 'B'},
		},
	},

	'purpleair_um_particles_per_100ml': {
		'HELP': 'Count concentration (particles/100ml) of all particles greater than or equal to label µm in diameter.',
		'TYPE': 'gauge',
		'UNIT': 'particles_per_100ml',
		'fields': {
			'0.3_um_count_a': {'channel': 'A', 'um': '0.3'},
			'0.3_um_count_b': {'channel': 'B', 'um': '0.3'},
			'0.5_um_count_a': {'channel': 'A', 'um': '0.5'},
			'0.5_um_count_b': {'channel': 'B', 'um': '0.5'},
			'1.0_um_count_a': {'channel': 'A', 'um': '1.0'},
			'1.0_um_count_b': {'channel': 'B', 'um': '1.0'},
			'2.5_um_count_a': {'channel': 'A', 'um': '2.5'},
			'2.5_um_count_b': {'channel': 'B', 'um': '2.5'},
			'5.0_um_count_a': {'channel': 'A', 'um': '5.0'},
			'5.0_um_count_b': {'channel': 'B', 'um': '5.0'},
			'10.0_um_count_a': {'channel': 'A', 'um': '10.0'},
			'10.0_um_count_b': {'channel': 'B', 'um': '10.0'},
		},
	},

	'purpleair_wifi_rssi': {
		'HELP': 'The WiFi signal strength.',
		'TYPE': 'gauge',
		'UNIT': 'rssi',
		'fields': {
			'rssi': {},
		},
	},

	'purpleair_latency_seconds': {
		'HELP': 'The time taken to send data to the PurpleAir servers.',
		'TYPE': 'gauge',
		'UNIT': 'seconds',
		'fields': {
			'pa_latency': {},
		},
		'normalize': lambda field, x : x / 1000,
	},

	'purpleair_uptime_seconds': {
		'HELP': 'The time since the firmware started as last reported by the sensor.',
		'TYPE': 'gauge',
		'UNIT': 'seconds',
		'fields': {
			'uptime': {},
		},
		'normalize': lambda field, x : x * 60,
	},

}

#
# Helper Functions
#

def calc_epa_aqi(field: str, value: float) -> float:
	"""
	Calculates the US EPA AQI index for the given raw pollutant value based on:
	https://www.airnow.gov/sites/default/files/2020-05/aqi-technical-assistance-document-sept2018.pdf

	Currently only supports PM2.5 and PM10.

	```
	:return: The US EPA AQI index
	:rtype: float
	```
	"""
	pollutant = field.upper().split('_')[0]
	match pollutant:
		case 'PM2.5':
			breakpoint_pollutant = [ 12.0, 35.4, 55.4, 150.4, 250.4, 350.4, 500.4 ]
		case 'PM10.0':
			breakpoint_pollutant = [ 54, 154, 254, 354, 424, 504, 604 ]
		case 'O3' | 'CO' | 'SO2' | 'NO2':
			raise ValueError(f'{pollutant} is not currently supported.')
		case _:
			raise ValueError(f'{field} could not be parsed into a valid pollutant.')

	breakpoint_aqi = [ 50, 100, 150, 200, 300, 400, 500 ]

	# First clamp based on min and max
	if value <= 0:
		return 0;
	if value >= breakpoint_pollutant[6]:
		return breakpoint_aqi[6];

	# Walk breakpoints and calculate based on ratios
	for index, bp in enumerate(breakpoint_pollutant):
		if value <= bp:
			break;

	i_lo = 0
	bp_lo = 0
	i_hi =  breakpoint_aqi[index]
	bp_hi = breakpoint_pollutant[index]

	if index > 0:
		i_lo =  breakpoint_aqi[index-1]
		bp_lo = breakpoint_pollutant[index-1]

	return (i_hi - i_lo) / (bp_hi - bp_lo) * ( value - bp_lo ) + i_lo

def get_fields() -> list:
	"""
	Gets all fields we need to query the PurpleAir API for based on configured metrics.

	```
	:return: Fields needed from the PurpleAir API
	:rtype: list
	```
	"""
	fields = []

	# Metric fields
	for metric_name, metric_def in METRICS.items():
		fields = list(set(fields + list(metric_def['fields'].keys())))

	# Info metric fields
	for info_name, info_fields in INFO_FIELDS.items():
		fields = list(set(fields + info_fields))

	return fields

def query_api(sensor: int) -> dict:
	if sensor in _cache:
		if 'time_stamp' in _cache[sensor] and time.time() - _cache[sensor]['time_stamp'] < int(_conf.get('api_cache_time')):
			return _cache[sensor]
		else:
			_cache[sensor]['time_stamp'] = time.time() # stampede protection
	else:
		_cache[sensor] = {}

	response = _session.get(
		f"{_conf.get('api_endpoint')}/{sensor}",
		params = {
			'fields': ','.join(get_fields()),
		}
	)

	if response.status_code == 200:
		_cache[sensor] = response.json()
	
	return _cache[sensor]

def to_label_param(labels: dict) -> str:
	params = []
	for label_name, label_value in labels.items():
		escaped = str(label_value).replace('\\','\\\\').replace('"','\\"')
		params.append(f'{label_name}="{escaped}"')
	return ','.join(params)

def collect_sensor(sensor: int, exposition: dict) -> None:
	data = query_api(sensor)

	if 'time_stamp' not in data or 'sensor' not in data:
		return

	# Metric fields
	for metric_name, metric_def in METRICS.items():
		for field_name, labels in metric_def['fields'].items():
			if field_name not in data['sensor']:
				_logger.debug("Did not find a value for: %s", field_name)
				continue

			# Add in sensor id
			labels['sensor'] = sensor

			# See if we need to normalize the value
			if 'normalize' in metric_def:
				value = metric_def['normalize'](
					field_name,
					data['sensor'][field_name]
				)
			else:
				value = data['sensor'][field_name]

			if metric_name not in exposition:
				exposition[metric_name] = []

			exposition[metric_name].append("%s{%s} %f %i" % (
				metric_name,
				to_label_param(labels),
				value,
				data['data_time_stamp'] * 1000
			))

	# Info fields
	for info_name, info_fields in INFO_FIELDS.items():
		labels = {
			'sensor': sensor,
		}
		for field_name in info_fields:
			if field_name not in data['sensor']:
				_logger.debug("Did not find a value for: %s", field_name)
				continue
			labels[field_name] = data['sensor'][field_name]

		if info_name not in exposition:
			exposition[info_name] = []

		exposition[info_name].append("%s{%s} %f %i" % (
			info_name,
			to_label_param(labels),
			1,
			data['data_time_stamp'] * 1000
		))

def collect() -> list:
	exposition={}
	for sensor in _conf.get('sensor_ids').split(','):
		collect_sensor(int(sensor), exposition)

	output = []

	# Info fields
	for info_name in INFO_FIELDS.keys():
		if info_name not in exposition:
			exposition[info_name] = []

		output.append("# TYPE %s info" % (
			info_name.replace('_info', '')
		))

		output += exposition[info_name]
		output.append('')

	# Metric fields
	for metric_name, metric_def in METRICS.items():
		if metric_name not in exposition:
			exposition[metric_name] = []

		for desc in [ 'TYPE', 'UNIT', 'HELP' ]:
			if desc in metric_def:
				output.append("# %s %s %s" % (
					desc,
					metric_name,
					metric_def[desc]
				))
		output += exposition[metric_name]
		output.append('')

	return output
