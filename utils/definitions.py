
SEPARATOR = [0x0A, 0x0D]

#engine commands
ID_SET_POWER_MODE_EC = 0x22
ID_SET_ENGINE_STATE_EC = 0x23 # the docs say 0x03 but that is already used for the FC...
ID_FIRE_ROCKET_EC = 0x2F
#engine returns
ID_SOFTWARE_STATE_EC = 0x30
ID_HARDWARE_STATE_EC =  0x31
ID_RETURN_POWER_MODE_EC = 0x32
ID_RETURN_ENGINE_STATE_EC = 0x33
ID_FIRE_ROCKET_CONFIRMATION_EC = 0x3F

#flight commands
ID_TIME_SYNC_FC = 0x00
ID_SET_POWER_MODE_FC =0x01
ID_SET_RADIO_EQUIPMENT_FC = 0x02
ID_SET_PARACHUTE_OUTPUT_FC = 0x03
#flight returns
ID_RETURN_TIME_SYNC_FC = 0x10
ID_RETURN_POWER_MODE_FC = 0x11
ID_RETURN_RADIO_EQUIPMENT_FC = 0x12
ID_RETURN_PARACHUTE_OUTPUT_FC = 0x13
ID_ONBOARD_BATTERY_VOLTAGE_FC = 0x14
ID_GNSS_DATA_FC = 0x15
ID_FLIGHT_CONTROLLER_STATUS_FC = 0x16

#flight telemetry
ID_MS_SINCE_BOOT_FC = 0x40
ID_US_SINCE_BOOT_FC = 0x41
ID_GNSS_DATA_1_FC = 0x43
ID_GNSS_DATA_2_FC =0x44
ID_INSIDE_TEMPERATURE_FC = 0x45
ID_INSIDE_PRESSURE_FC = 0x46
ID_IMU_1_FC = 0x47
ID_IMU_2_FC = 0x48
ID_EXTERNAL_TEMPERATURE_FC = 0x49
ID_AIR_SPEED_FC = 0x4A
ID_ONBOARD_BATTERY_VOLTAGE_TM_FC = 0x4B
ID_FLIGHT_CONTROLLER_STATUS_TM_FC = 0x4C

ID_TIMESTAMP = 0x00 # timestamp for the backup file