import sys, os, time, logging
import clr 
from System import Decimal, Char
from System.Collections.Generic import List

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

    # def pick_device(self, device_address):
    #     boolean = self.controller.ReaddressDevice(device_address)
    #     if boolean == True: 
    #         if device_address not in self.device_address: 
    #             self.device_address.append(device_address)
    #     else: 
    #         logger.error('Failed to pick device')
        
    def connect(self, com_port): 
       ELLDevicePort.Connect(com_port) # com_port=COM12        
           
       elliptec = self.controller.ScanAddresses(self.min_add, self.max_add)
       
       logger.info(f'Connected to Elliptec device at {com_port}')
       
       for device in elliptec: 
           if self.controller.Configure(device): 
                self.elliptec_list = self.controller.AddressedDevice(device[0])
                self.device_address.append(self.convert_to_char(self.elliptec_list.Address))
                self.device_info = self.elliptec_list.DeviceInfo
                for stri in self.device_info.Description():
                    print(stri)

    def convert_to_char(self, address): 
        char_list = List[Char]()
        char_list.Add(Char.Parse(address))
        return char_list

    #ELLBaseDevice or ELLDevices? 
    def move_abs(self, actuator, value): 
        boolean = self.elliptec_list.MoveAbsolute(self.device_address[actuator-1], Decimal(value)) # DK - I think the first attribute should be '1'/'2' or 1/2 because this is supposed to be 'address' in the documentation. 
        return boolean
    
    def move_rel(self, actuator, value): 
        boolean = self.elliptec_list.MoveRelative(self.device_address[actuator-1], Decimal(value))
        return boolean
    
    def home(self, actuator): 
        if "LinearStage" in self.get_device_type:
            boolean = self.elliptec_list.Home(self.device_address[actuator-1], ELLBaseDevice.DeviceDirection.Linear)
            return boolean
        elif "RotaryStage" in self.get_device_type:
            boolean = self.elliptec_list.Home(self.device_address[actuator-1], ELLBaseDevice.DeviceDirection.Clockwise)
            return boolean
        else:
            logger.error(f'Unknown device type: {self.get_device_type}')

    def get_position(self): 
        logger.info(f'Current position: {self.elliptec_list.GetPosition()}')
        return float(str(self.elliptec_list.get_Position()))

    def get_device_type(self, actuator): 
        """Get the device type of the connected device"""
        return str(self.device_info.get_DeviceType()) +  str(actuator)

    def get_units(self):  # DK - add address 
        return self.device_info.Units