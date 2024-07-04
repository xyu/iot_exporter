IoT Exporter for Prometheus
===========================

Exposes metrics from various IoT stuff for Prometheus. Currently supports:

 - PurpleAir

## Exporter Details

<details>
<summary>PurpleAir Exporter</summary>

### About

The exporter queries the PurpleAir API and caches the results so that the exporter endpoint may be queried for more frequently without adversely impacting PurpleAir API points consumption. Data freshness is also checked before a full metrics query against the PurpleAir API to avoid consuming API points for stale data that's already in cache. Finally, metrics are exported with the actual data timestamp to more accurately reflect when the data was collected by the sensor.

### Metrics Sample

```
# TYPE purpleair_device_info gauge
purpleair_device_info{sensor="888888",name="Ladd’s Addition",model="PA-II-FLEX",hardware="3.0+OPENLOG+31037 MB+DS3231+BME280+BME68X+PMSX003-A+PMSX003-B",firmware_version="7.04"} 1.000000 1720116254000
purpleair_device_info{sensor="999999",name="Alphabet District",model="PA-II-FLEX",hardware="3.0+OPENLOG+32044 MB+RV3028+BME68X+KX122+PMSX003-A+PMSX003-B",firmware_version="7.04"} 1.000000 1720116254000

# TYPE purpleair_location_info gauge
purpleair_location_info{sensor="888888",location_type="0",longitude="...",latitude="...",altitude="..."} 1.000000 1720116254000
purpleair_location_info{sensor="999999",location_type="0",longitude="...",latitude="...",altitude="..."} 1.000000 1720116254000

# TYPE purpleair_confidence_ratio gauge
# UNIT purpleair_confidence_ratio ratio
# HELP purpleair_confidence_ratio The average of confidence_manual and confidence_auto indicating how closely channel A and B pseudo averages match each other.
purpleair_confidence_ratio{sensor="888888"} 1.000000 1720116378000
purpleair_confidence_ratio{sensor="999999"} 1.000000 1720116423000

# TYPE purpleair_humidity_ratio gauge
# UNIT purpleair_humidity_ratio ratio
# HELP purpleair_humidity_ratio Relative humidity inside of the sensor housing.
purpleair_humidity_ratio{channel="A",sensor="888888"} 0.420000 1720116378000
purpleair_humidity_ratio{channel="B",sensor="888888"} 0.390000 1720116378000
purpleair_humidity_ratio{channel="A",sensor="999999"} 0.390000 1720116423000
purpleair_humidity_ratio{channel="B",sensor="999999"} 0.390000 1720116423000

# TYPE purpleair_temperature_fahrenheit gauge
# UNIT purpleair_temperature_fahrenheit fahrenheit
# HELP purpleair_temperature_fahrenheit Temperature inside of the sensor housing.
purpleair_temperature_fahrenheit{channel="A",sensor="888888"} 76.000000 1720116378000
purpleair_temperature_fahrenheit{channel="B",sensor="888888"} 74.000000 1720116378000
purpleair_temperature_fahrenheit{channel="A",sensor="999999"} 73.000000 1720116423000
purpleair_temperature_fahrenheit{channel="B",sensor="999999"} 73.000000 1720116423000

# TYPE purpleair_pressure_millibars gauge
# UNIT purpleair_pressure_millibars millibars
# HELP purpleair_pressure_millibars Current pressure in Millibars.
purpleair_pressure_millibars{channel="A",sensor="888888"} 1021.970000 1720116378000
purpleair_pressure_millibars{channel="B",sensor="888888"} 1020.660000 1720116378000
purpleair_pressure_millibars{channel="A",sensor="999999"} 1018.590000 1720116423000
purpleair_pressure_millibars{channel="B",sensor="999999"} 1018.590000 1720116423000

# TYPE purpleair_voc gauge
# HELP purpleair_voc VOC concentration (IAQ) in Bosch static iaq units as per BME680 spec sheet, EXPERIMENTAL.
purpleair_voc{channel="B",sensor="888888"} 50.000000 1720116378000
purpleair_voc{channel="B",sensor="999999"} 60.210000 1720116423000

# TYPE purpleair_pm_aqi gauge
# HELP purpleair_pm_aqi US EPA AQI based on PM2.5 / PM10 particulate concentrations
purpleair_pm_aqi{channel="A",pm="2.5",sensor="888888"} 21.250000 1720116378000
purpleair_pm_aqi{channel="B",pm="2.5",sensor="888888"} 17.500000 1720116378000
purpleair_pm_aqi{channel="A",pm="10.0",sensor="888888"} 8.148148 1720116378000
purpleair_pm_aqi{channel="B",pm="10.0",sensor="888888"} 7.222222 1720116378000
purpleair_pm_aqi{channel="A",pm="2.5",sensor="999999"} 17.083333 1720116423000
purpleair_pm_aqi{channel="B",pm="2.5",sensor="999999"} 19.166667 1720116423000
purpleair_pm_aqi{channel="A",pm="10.0",sensor="999999"} 6.574074 1720116423000
purpleair_pm_aqi{channel="B",pm="10.0",sensor="999999"} 7.129630 1720116423000

# TYPE purpleair_pm_concentration_ug_per_m3 gauge
# UNIT purpleair_pm_concentration_ug_per_m3 ug_per_m3
# HELP purpleair_pm_concentration_ug_per_m3 Estimated mass concentration (µg/m³) of PM1 / PM2.5 / PM10 particulates with a diameter of fewer than 1 / 2.5 / 10 microns.
purpleair_pm_concentration_ug_per_m3{channel="A",pm="1.0",sensor="888888"} 5.500000 1720116378000
purpleair_pm_concentration_ug_per_m3{channel="B",pm="1.0",sensor="888888"} 6.200000 1720116378000
purpleair_pm_concentration_ug_per_m3{channel="A",pm="2.5",sensor="888888"} 5.100000 1720116378000
purpleair_pm_concentration_ug_per_m3{channel="B",pm="2.5",sensor="888888"} 4.200000 1720116378000
purpleair_pm_concentration_ug_per_m3{channel="A",pm="10.0",sensor="888888"} 8.800000 1720116378000
purpleair_pm_concentration_ug_per_m3{channel="B",pm="10.0",sensor="888888"} 7.800000 1720116378000
purpleair_pm_concentration_ug_per_m3{channel="A",pm="1.0",sensor="999999"} 5.600000 1720116423000
purpleair_pm_concentration_ug_per_m3{channel="B",pm="1.0",sensor="999999"} 5.000000 1720116423000
purpleair_pm_concentration_ug_per_m3{channel="A",pm="2.5",sensor="999999"} 4.100000 1720116423000
purpleair_pm_concentration_ug_per_m3{channel="B",pm="2.5",sensor="999999"} 4.600000 1720116423000
purpleair_pm_concentration_ug_per_m3{channel="A",pm="10.0",sensor="999999"} 7.100000 1720116423000
purpleair_pm_concentration_ug_per_m3{channel="B",pm="10.0",sensor="999999"} 7.700000 1720116423000

# TYPE purpleair_visual_range_meters gauge
# UNIT purpleair_visual_range_meters meters
# HELP purpleair_visual_range_meters Often referred to as visibility, visual range is the distance from the observer that a large dark object, e.g. a mountain top or large building, just disappears from view.
purpleair_visual_range_meters{channel="A",sensor="888888"} 123776.123903 1720116378000
purpleair_visual_range_meters{channel="B",sensor="888888"} 123394.292223 1720116378000
purpleair_visual_range_meters{channel="A",sensor="999999"} 122038.989893 1720116423000
purpleair_visual_range_meters{channel="B",sensor="999999"} 129047.201496 1720116423000

# TYPE purpleair_light_scattering_deciviews gauge
# UNIT purpleair_light_scattering_deciviews deciviews
# HELP purpleair_light_scattering_deciviews A haze index related to light scattering and extinction that is approximately linearly related to human perception of the haze.
purpleair_light_scattering_deciviews{channel="A",sensor="888888"} 11.476723 1720116378000
purpleair_light_scattering_deciviews{channel="B",sensor="888888"} 11.507619 1720116378000
purpleair_light_scattering_deciviews{channel="A",sensor="999999"} 11.618062 1720116423000
purpleair_light_scattering_deciviews{channel="B",sensor="999999"} 11.059685 1720116423000

# TYPE purpleair_um_particles_per_100ml gauge
# UNIT purpleair_um_particles_per_100ml particles_per_100ml
# HELP purpleair_um_particles_per_100ml Count concentration (particles/100ml) of all particles greater than or equal to label µm in diameter.
purpleair_um_particles_per_100ml{channel="A",um="0.3",sensor="888888"} 1103.000000 1720116378000
purpleair_um_particles_per_100ml{channel="B",um="0.3",sensor="888888"} 1108.000000 1720116378000
purpleair_um_particles_per_100ml{channel="A",um="0.5",sensor="888888"} 317.000000 1720116378000
purpleair_um_particles_per_100ml{channel="B",um="0.5",sensor="888888"} 327.000000 1720116378000
purpleair_um_particles_per_100ml{channel="A",um="1.0",sensor="888888"} 49.000000 1720116378000
purpleair_um_particles_per_100ml{channel="B",um="1.0",sensor="888888"} 31.000000 1720116378000
purpleair_um_particles_per_100ml{channel="A",um="2.5",sensor="888888"} 3.000000 1720116378000
purpleair_um_particles_per_100ml{channel="B",um="2.5",sensor="888888"} 2.000000 1720116378000
purpleair_um_particles_per_100ml{channel="A",um="5.0",sensor="888888"} 1.000000 1720116378000
purpleair_um_particles_per_100ml{channel="B",um="5.0",sensor="888888"} 1.000000 1720116378000
purpleair_um_particles_per_100ml{channel="A",um="10.0",sensor="888888"} 0.000000 1720116378000
purpleair_um_particles_per_100ml{channel="B",um="10.0",sensor="888888"} 0.000000 1720116378000
purpleair_um_particles_per_100ml{channel="A",um="0.3",sensor="999999"} 1126.000000 1720116423000
purpleair_um_particles_per_100ml{channel="B",um="0.3",sensor="999999"} 1037.000000 1720116423000
purpleair_um_particles_per_100ml{channel="A",um="0.5",sensor="999999"} 319.000000 1720116423000
purpleair_um_particles_per_100ml{channel="B",um="0.5",sensor="999999"} 295.000000 1720116423000
purpleair_um_particles_per_100ml{channel="A",um="1.0",sensor="999999"} 30.000000 1720116423000
purpleair_um_particles_per_100ml{channel="B",um="1.0",sensor="999999"} 44.000000 1720116423000
purpleair_um_particles_per_100ml{channel="A",um="2.5",sensor="999999"} 1.000000 1720116423000
purpleair_um_particles_per_100ml{channel="B",um="2.5",sensor="999999"} 3.000000 1720116423000
purpleair_um_particles_per_100ml{channel="A",um="5.0",sensor="999999"} 0.000000 1720116423000
purpleair_um_particles_per_100ml{channel="B",um="5.0",sensor="999999"} 0.000000 1720116423000
purpleair_um_particles_per_100ml{channel="A",um="10.0",sensor="999999"} 0.000000 1720116423000
purpleair_um_particles_per_100ml{channel="B",um="10.0",sensor="999999"} 0.000000 1720116423000

# TYPE purpleair_wifi_rssi gauge
# UNIT purpleair_wifi_rssi rssi
# HELP purpleair_wifi_rssi The WiFi signal strength.
purpleair_wifi_rssi{sensor="888888"} -76.000000 1720116378000
purpleair_wifi_rssi{sensor="999999"} -86.000000 1720116423000

# TYPE purpleair_latency_seconds gauge
# UNIT purpleair_latency_seconds seconds
# HELP purpleair_latency_seconds The time taken to send data to the PurpleAir servers.
purpleair_latency_seconds{sensor="888888"} 0.244000 1720116378000
purpleair_latency_seconds{sensor="999999"} 0.492000 1720116423000

# TYPE purpleair_uptime_seconds gauge
# UNIT purpleair_uptime_seconds seconds
# HELP purpleair_uptime_seconds The time since the firmware started as last reported by the sensor.
purpleair_uptime_seconds{sensor="888888"} 689460.000000 1720116378000
purpleair_uptime_seconds{sensor="999999"} 186840.000000 1720116423000

# TYPE purpleair_api_requests_total counter
# HELP purpleair_api_requests_total Count of API requests made and skipped due to existing cache
purpleair_api_requests_total{cache="hit"} 60.000000
purpleair_api_requests_total{cache="miss"} 16.000000

# EOF
```
</details>
