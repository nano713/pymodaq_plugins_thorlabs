import clr
import sys
import numpy as np

from System import Decimal
from System import Action
from System import UInt64
from System import UInt32

import logging

ccs_path = 'C:\\Program Files\\Thorlabs\\ThorSpectra'
sys.path.append(ccs_path)

clr.AddReference("ThorlabsOSAWrapper")

import ThorlabsOSAWrapper.LibDeviceInterface as LibDeviceInterface
import ThorlabsOSAWrapper.DeviceLocator as DeviceLocator
# import ThorlabsOSAWrapper.SpectrumStruct as SpectrumStruct

DeviceLocator.InitializeSpectrometers()
numberOfOSAs = DeviceLocator.GetInstrumentNum()

serialNumbers = []
osaInterfaces = []
for i in range(numberOfOSAs):
    osaInterfaces = osaInterfaces.append(LibDeviceInterface(i))
    serialNumbers.append(osaInterfaces[i].InstrumentDescription.GetSerial())

logging.info(f"Found {numberOfOSAs} CCS devices with serial numbers: {serialNumbers}")

class CCS:
    def __init__(self, serial):
        self._device = None
        self.serial = serial

    def connect(self):
        for i in range(len(serialNumbers)):
            if self.serial == serialNumbers[i]:
                self._device = osaInterfaces[i]

    def close(self):
        """
            close the current instance of CCS instrument.
        """
        DeviceLocator.StopAllRetrievalsOnGUIClose()

    def get_wavelength(self):
        wavelength = self.SpectrumStruct.GetXArray()
        return np.array(wavelength)


    def acquire_single_spectrum(self):
        intensity =  self._device.AcquireSingleSpectrum()
        return np.array(intensity)

    def set_exposure_time(self, time):
        self._device.SetExposureTime(time)


