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
        self.device_info = None
        self.elliptec_list = []
        self.min_add = '0'
        self.max_add = 'F'
        self.device_address = []

    def pick_device(self, device_address):
        boolean = self.controller.ReaddressDevice(device_address)
        if boolean == True: 
            if device_address not in self.device_address: 
                self.device_address.append(device_address)
        else: 
            logger.error('Failed to pick device')
        

    
    def connect(self, com_port): 
       ELLDevicePort.Connect(com_port) # com_port=COM12        
           
       elliptec = self.controller.ScanAddresses(self.min_add, self.max_add)
       logger.info(f'Connected to Elliptec device at {com_port}')
       
       for device in elliptec: 
           if self.controller.Configure(device): 
                self.elliptec_list = self.controller.AddressedDevice(device[0])
                self.device_info = self.elliptec_list.DeviceInfo
                for stri in self.device_info.Description():
                    print(stri)
                #logger.info(f'Device info: {device_info}')

    #ELLBaseDevice or ELLDevices? 
    def move_abs(self, actuator, value): 
        self.elliptec_list.MoveAbsolute(self.device_address[actuator-1], Decimal(value))
    
    def move_rel(self, actuator, value): 
        self.elliptec_list.MoveRelative(self.device_address[actuator-1], Decimal(value))
    
    def home(self, actuator): 
        if self.get_device_type == "LinearStage":
            self.elliptec_list.Home(self.device_address[actuator-1], ELLBaseDevice.DeviceDirection.Linear)
        elif self.get_device_type == "RotaryStage":
            self.elliptec_list.Home(self.device_address[actuator-1], ELLBaseDevice.DeviceDirection.Clockwise)
        else:
            logger.error(f'Unknown device type: {self.get_device_type}')

    def get_position(self): 
        logger.info(f'Current position: {self.elliptec_list.GetPosition()}')
        return float(str(self.elliptec_list.get_Position()))

    def get_device_type(self, actuator): 
        """Get the device type of the connected device"""
        return str(self.device_info.get_DeviceType()) + str(actuator)

    def get_units(self): 
        return self.device_info.Units
            
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