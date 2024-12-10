
import ctypes
import os
import time

from _ctypes import byref

# define dll path(dynamic link library)
dll_path = r"C:\Program Files\IVI Foundation\VISA\Win64\Bin"
# change directory to the dll path.
os.chdir(dll_path)
# This line loads the DLL file named "TLUp_64.dll" using the ctypes library.
lib=ctypes.cdll.LoadLibrary("TLUp_64.dll")
# AK question:from where this TLUp_64.dll file is there in bin folder?
class UPLEDXXX:
    def __init__(self, lib_path, resource_name):
        self.lib = ctypes.cdll.LoadLibrary(lib_path)
        self.resource_name = resource_name
        self.Upled_handle = ctypes.c_int(0)
    # def __init__(self, resource_name):
        # self.dll_path = r"C:\Program Files\IVI Foundation\VISA\Win64\Bin"  # DK - Replace dll_path with C://Program Files//IVI Foundation//VISA//Win64//Bin...?
        # self.resource_name = resource_name#.encode('utf-8')
        # self.lib = None
        # self.Upled_handle = ctypes.c_int(0)
        # def load_library(self):
        # os.chdir(self.dll_path)
        # self.lib = ctypes.cdll.LoadLibrary("TLCCS_64.dll")
    def count_devices(self):
        # Count upSeries devices
        device_count = ctypes.c_uint32()
        self.lib.TLUP_findRsrc(0, byref(device_count))
        if device_count.value > 0:
            return f"Number of upSeries devices found: {device_count.value}"
        else:
            return "No upSeries devices found."

    def connect(self):
        # Connect to the device using DLL's init function
        self._device = self.lib.tlUpled_init(self.resource_name, 1, 1, ctypes.byref(self.Upled_handle))
        if self._device != 0:
            raise Exception("Failed to initialize the device")

        # Retrieve model name and serial number
        self.model_name = ctypes.create_string_buffer(256)
        self.serial_number = ctypes.create_string_buffer(256)
        self.lib.TLUP_getRsrcInfo(0, 0, self.model_name, self.serial_number, 0, 0)

        return {
            "model_name": self.model_name.value.decode(),
            "serial_number": self.serial_number.value.decode()
        }

    def initialize_first_device(self):
        # Initialize the first connected upSeries device
        up_name = ctypes.create_string_buffer(256)
        self.lib.TLUP_getRsrcName(0, 0, up_name)
        up_handle = ctypes.c_int(0)
        res = self.lib.TLUP_init(up_name.value, 0, 0, byref(up_handle))
        if res != 0:
            raise Exception("Failed to initialize the first upSeries device")

        # If the device is an upLED, execute this section
        if self.model_name.value.decode() == "upLED":
            # Enable the use of LEDs without EEPROM (non-Thorlabs or unmounted LEDs)
            self.lib.TLUP_setLedUseNonThorlabsLed(up_handle, 1)

            # Make sure the LED is switched off (0 = off, 1 = on)
            self.lib.TLUP_switchLedOutput(up_handle, 0)

            # Get information about the connected LED
            current_setpoint = ctypes.c_double()
            led_name = ctypes.create_string_buffer(256)
            led_serial_number = ctypes.create_string_buffer(256)
            led_current_limit = ctypes.c_double()
            led_forward_voltage = ctypes.c_double()


            self.lib.TLUP_getLedInfo(up_handle, led_name, led_serial_number, byref(led_current_limit),
                                     byref(led_forward_voltage))

            return {
                "led_name": led_name.value.decode(),
                "led_serial_number": led_serial_number.value.decode(),
                "led_current_limit": led_current_limit.value,
                "led_forward_voltage": led_forward_voltage.value,
                "led_wavelength": led_wavelength.value
            }
        else:
            return "The connected device is not an upLED."



    # def connect(self):
    #     # connect to the device using DLL's init function'
    #     self.lib.TLUP_getRsrcInfo(0, 0, self.model_name, self.serial_number, 0, 0)
    #     print("Connecting to this device:")
    #     print("Model name: ", self.model_name.value.decode(), ", Serial number: ", self.serial_number.value.decode())
    #     print()
    def close(self):
        lib.tlUpled_close(self.Upled_handle)
        # DK - replace pass with the command.

    #  self.lib.tlccs_close(self.ccs_handle)  # when writing your own plugin replace this line

# # Example usage
# if __name__ == "__main__":
#     spectrometer = UPLEDXXX('USB0::0x1313::0x8087::M00934802::RAW')
#     spectrometer.load_library()
#     spectrometer.connect()
#     spectrometer.set_integration_time(10.0e-3)
#     spectrometer.start_scan()
#     wavelengths = spectrometer.get_wavelength_data()