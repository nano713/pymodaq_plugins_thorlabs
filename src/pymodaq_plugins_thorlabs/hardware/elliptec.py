import sys, os, time, logging
import clr 
from System import Decimal

logger = logging.getLogger(__name__)

elliptec_path = 'C:\\Program Files\\Thorlabs\\Elliptec'
sys.path.append(elliptec_path)

clr.AddReference("Thorlabs.Elliptec.ELLO_DLL")

from Thorlabs.Elliptec.ELLO_DLL import ELLDevicePort, ELLDevices, ELLBaseDevice, DeviceID # DK - is this correct? I thought ELLO_DLL class comes from dll.
                                                                                        # AD -> No. These are the classes. ELLO_DLL is the name of the dll not the class

class Elliptec: 
    def __init__(self): 
        self.controller = ELLDevices()
        self.device_type = []
        self.elliptec_list = []
        self.min_add = '0'
        self.max_add = 'F'
    
    def connect(self, com_port, device_type): 
       ELLDevicePort.Connect(com_port) # com_port=COM12
       DeviceID.DeviceTypes(device_type) # enable way for device_type to be read
       if device_type == 4: 
           
           
       elliptec = self.controller.ScanAddresses(self.min_add, self.max_add)
       logger.info(f'Connected to Elliptec device at {com_port}')

       for device in elliptec: 
           if device != None: 
            self.elliptec_list = ELLDevices.AddressedDevice(elliptec[0])
            device_info = self.elliptec_list.DeviceInfo()
            logger.info(f'Device info: {device_info}')

    #ELLBaseDevice or ELLDevices? 
    def move_abs(self, value): 
        self.elliptec_list.MoveAbsolute(Decimal(value))
    
    def move_rel(self, value): 
        self.elliptec_list.MoveRelative(Decimal(value))
    
    def home(self): 
        if self.devic # DK fix this line.
        self.elliptec_list.Home(ELLBaseDevice.DeviceDirection.Clockwise) # DK - in linear stage, we need ELLBaseDevice.DeviceDirection.Linear attribute. Can we address multiple device types?
    
    def get_position(self): 
        logger.info(f'Current position: {self.elliptec_list.GetPosition()}')
        return self.elliptec_list.GetPosition()

    def get_device_type(self): 
        # return string and value 
        return self.device_type
    def set_device_types(self, device_type): #device_type only 14 or 20 based on params
        self.device_type = DeviceID.DeviceTypes(device_type)

    def set_units(self): 
        if self.get_device_type() == 3 or 7: # make sure if ELL20 is 20, ELL14 is 14, etc
             DeviceID.UnitTypes('MM')
        elif self.get_device_type() == 4 or 8:
            DeviceID.UnitTypes('Degrees')
            
    # method to get device type
    
    # method to set units
    
    
    """
    some random idea (No: I hope you do not polish this)
    device_list = []
    for i in total_number_of_devices:
        device_list = ellDevices.AddressedDevice(device[i])
    
    device_list[axis_index] # to specify an axis.
    
    what do you think?
    """