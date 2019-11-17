import datetime

import pandas as pd


class GenericSensor:
    """ This is a generic class to deal with most sensors

    """

    def __init__(self, position, nb_samples, fields):
        self.position = position
        self.nb_samples = nb_samples
        self.fields = fields
        self.sample_size = sum( (field['size'] for _, field in self.fields.items()) )  # Byte

        self.set_default_values()

    def set_default_values(self):
        columns = ['Time'] + list(self.fields.keys())
        self.raw_data = pd.DataFrame(columns=columns)

    def extract_samples(self, frame):
        samples = frame[self.position:self.position +
                        self.sample_size*self.nb_samples]
        return samples

    def get_field_value(self, sample, field):
        start = self.fields[field]['start']
        size = self.fields[field]['size']
        byte_order = self.fields[field]['byte_order']
        signed = self.fields[field]['signed']
        convert = self.fields[field]['conversion_function']

        value_bytes = sample[start: start + size]
        value_int = int.from_bytes(value_bytes, byte_order, signed=signed)
        value = convert(value_int)

        return value

    def update_raw_data(self, frame, time):
        samples = self.extract_samples(frame)

        for i in range(self.nb_samples):
            sample = samples[i*self.sample_size: (i+1)*self.sample_size]

            time_value = {'Time': time}
            raw_values = {field: self.get_field_value(
                sample, field) for field in self.fields.keys()}
            values = {**time_value, **raw_values}

            self.raw_data = self.raw_data.append(values, ignore_index=True)


class RTC(GenericSensor):
    fields = {
        'hour': {
            'start': 0,
            'size': 1,  # Byte
            'conversion_function': lambda x: x,  # h
            'byte_order': 'big',
            'signed': False,
        },
        'minute': {
            'start': 1,
            'size': 1,
            'conversion_function': lambda x: x,  # min
            'byte_order': 'big',
            'signed': False,
        },
        'second': {
            'start': 2,
            'size': 1,
            'conversion_function': lambda x: x,  # s
            'byte_order': 'big',
            'signed': False,
        },
        'millisecond': {
            'start': 3,
            'size': 1,
            'conversion_function': lambda x: x*1000/256.,  # ms
            'byte_order': 'big',
            'signed': False,
        },
    }

    def __init__(self, position, nb_samples):
        super().__init__(position, nb_samples, self.fields)

    def update_data(self, frame, time=None):
        self.update_raw_data(frame, time)
        print(self.raw_data)
    
    def get_last_time(self):
        hour = int(self.raw_data.hour.iloc[-1])
        minute = int(self.raw_data.minute.iloc[-1])
        second = int(self.raw_data.second.iloc[-1])
        microsecond = int(self.raw_data.millisecond.iloc[-1]*1000)
        last_time = datetime.time(hour, minute, second, microsecond)
        return last_time


class Timer(GenericSensor):
    fields = {
        'Timer': {
            'start': 0,
            'size': 4,  # Byte
            'conversion_function': lambda x: x*5e-4,  # s
            'byte_order': 'little',
            'signed': False,
        },
    }

    def __init__(self, position, nb_samples):
        super().__init__(position, nb_samples, self.fields)

    def update_data(self, frame, time=None):
        self.update_raw_data(frame, time)
        print(self.raw_data)


class Batteries(GenericSensor):
    fields = {
        'Battery1': {
            'start': 0,
            'size': 2,  # Byte
            'conversion_function': lambda x: x*3.3/4096*4.030,  # Volt
            'byte_order': 'little',
            'signed': False,
        },
        'Battery2': {
            'start': 2,
            'size': 2,
            'conversion_function': lambda x: x*3.3/4096*2.786,  # Volt
            'byte_order': 'little',
            'signed': False,
        },
    }

    def __init__(self, position, nb_samples):
        super().__init__(position, nb_samples, self.fields)

    def update_data(self, frame, time=None):
        self.update_raw_data(frame, time)
        print(self.raw_data)


class IMU(GenericSensor):
    fields = {
        'Acc_X': {
            'start': 0,
            'size': 2,  # Byte
            'conversion_function': lambda x: x/2048.,  # g
            'byte_order': 'big',
            'signed': True,
        },
        'Acc_Y': {
            'start': 2,
            'size': 2,
            'conversion_function': lambda x: x/2048.,  # g
            'byte_order': 'big',
            'signed': True,
        },
        'Acc_Z': {
            'start': 4,
            'size': 2,
            'conversion_function': lambda x: x/2048.,  # g
            'byte_order': 'big',
            'signed': True,
        },
        'Temp': {
            'start': 6,
            'size': 2,
            'conversion_function': lambda x: x/326.8 + 25,  # °C
            'byte_order': 'big',
            'signed': True,
        },
        'Gyro_X': {
            'start': 8,
            'size': 2,
            'conversion_function': lambda x: x/32.8,  # dps
            'byte_order': 'big',
            'signed': True,
        },
        'Gyro_Y': {
            'start': 10,
            'size': 2,
            'conversion_function': lambda x: x/32.8,  # dps
            'byte_order': 'big',
            'signed': True,
        },
        'Gyro_Z': {
            'start': 12,
            'size': 2,
            'conversion_function': lambda x: x/32.8,  # dps
            'byte_order': 'big',
            'signed': True,
        },
    }

    def __init__(self, position, nb_samples):
        super().__init__(position, nb_samples, self.fields)

    def update_data(self, frame, time=None):
        self.update_raw_data(frame, time)
        print(self.raw_data)


class BMP(GenericSensor):
    fields = {
        'Temperature': {
            'start': 0,
            'size': 4,  # Byte
            'conversion_function': lambda x: x/100.,  # °C
            'byte_order': 'little',
            'signed': True,
        },
        'Pressure': {
            'start': 4,
            'size': 4,
            'conversion_function': lambda x: x/256.,  # Pa
            'byte_order': 'little',
            'signed': True,
        },
    }

    def __init__(self, position, nb_samples):
        super().__init__(position, nb_samples, self.fields)

    def update_data(self, frame, time=None):
        self.update_raw_data(frame, time)
        print(self.raw_data)


class MAG(GenericSensor):
    fields = {
        'Mag_X': {
            'start': 0,
            'size': 2,  # Byte
            'conversion_function': lambda x: x/6842.,  # Gauss
            'byte_order': 'big',
            'signed': True,
        },
        'Mag_Y': {
            'start': 2,
            'size': 2,
            'conversion_function': lambda x: x/6842.,  # Gauss
            'byte_order': 'big',
            'signed': True,
        },
        'Mag_Z': {
            'start': 4,
            'size': 2,
            'conversion_function': lambda x: x/6842.,  # Gauss
            'byte_order': 'big',
            'signed': True,
        },
    }

    def __init__(self, position, nb_samples):
        super().__init__(position, nb_samples, self.fields)

    def update_data(self, frame, time=None):
        self.update_raw_data(frame, time)
        print(self.raw_data)


class PITOT(GenericSensor):
    fields = {
        'Pressure': {
            'start': 0,
            'size': 2,  # Byte
            'conversion_function': lambda x: (x - 1638.) / (14747. - 1638.) * 5. * 34474.,  # Pa
            'byte_order': 'big',
            'signed': False,
        },
    }

    def __init__(self, position, nb_samples):
        super().__init__(position, nb_samples, self.fields)

    def update_data(self, frame, time=None):
        self.update_raw_data(frame, time)
        print(self.raw_data)


class Sigmundr:
    """ Extract data from a Telemetry frame received from Sigmundr

    """

    def __init__(self):
        self.rtc = RTC(4, 1)
        self.timer = Timer(8, 1)
        self.batteries = Batteries(12, 1)
        self.imu = IMU(16, 4)
        self.bmp2 = BMP(72, 1)
        self.bmp3 = BMP(80, 1)
        self.mag = MAG(88, 1)
        self.pitot = PITOT(92, 1)

    def update_sensors(self, frame):
        self.rtc.update_data(frame)
        time = self.rtc.get_last_time()
        self.timer.update_data(frame, time)
        self.batteries.update_data(frame, time)
        self.imu.update_data(frame, time)
        self.bmp2.update_data(frame, time)
        self.bmp3.update_data(frame, time)
        self.mag.update_data(frame, time)
        self.pitot.update_data(frame, time)
