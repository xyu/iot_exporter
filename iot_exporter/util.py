"""
Util functions used across different exporters.
"""

import configparser
import logging
import os 

_logger = logging.getLogger(__name__)
_config = None

def get_conf() -> configparser.ConfigParser:
	"""
	Handles getting configs for this app.

	```
	:return: The configs
	:rtype: configparser.ConfigParser
	```
	"""
	global _config
	if _config is None:
		from pkg_resources import resource_filename

		_config = configparser.ConfigParser()
		config_files_read = _config.read([
			resource_filename('iot_exporter', 'default.ini'),
			f'{os.getcwd()}/iot_exporter.ini',
			os.path.expanduser('~/.iot_exporter.ini'),
		])
		_logger.debug("Loaded the following config files: %s", config_files_read)
	return _config

def to_label_param(labels: dict) -> str:
	params = []
	for label_name, label_value in labels.items():
		escaped = str(label_value).replace('\\','\\\\').replace('"','\\"')
		params.append(f'{label_name}="{escaped}"')
	return ','.join(params)
