import sys, os, time, logging
import clr 
from System import Decimal

logger = logging.getLogger(__name__)

elliptec_path = 'C:\\Program Files\\Thorlabs\\Elliptec'
sys.path.append(elliptec_path)

clr.AddReference("Thorlabs.Elliptec.ELLO_DLL")

from Thorlabs.Elliptec.ELLO_DLL import ELLDevicePort, ELLDevices, ELLBaseDevice

class Elliptec: 
    def __init__(self): 
        self.controller = ELLDevices()
        self.elliptec_address = None
        self.min_add = '0'
        self.max_add = 'F'
    
    def connect(self, com_port): 
       ELLDevicePort.Connect(com_port)
       elliptec = self.controller.ScanAddresses(self.min_add, self.max_add)
       logger.info(f'Connected to Elliptec device at {com_port}')

       if elliptec in device: 
           if device[0] != None: 
            self.elliptec_address = ELLDevices.AddressedDevice(elliptec)
            device_info = self.elliptec_address.DeviceInfo()
            logger.info(f'Device info: {device_info}')

    #ELLBaseDevice or ELLDevices? 
    def move_abs(self, value): 
        self.elliptec_address.MoveAbsolute(Decimal(value))
    
    def move_rel(self, value): 
        self.elliptec_address.MoveRelative(Decimal(value))
    
    def home(self): 
        self.elliptec_address.Home(ELLBaseDevice.DeviceDirection.Clockwise)
    
    def get_psotion(self): 
        logger.info(f'Current position: {self.elliptec_address.GetPosition()}')
        return self.elliptec_address.GetPosition()
       
