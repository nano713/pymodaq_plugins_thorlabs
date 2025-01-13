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
        self.device_info = []
        self.elliptec_list = []
        self.min_add = '0'
        self.max_add = 'F'
        self.device_address = []
        self.units = []
    
    def connect(self, com_port): 
       ELLDevicePort.Connect(com_port) # com_port=COM12        
           
       elliptec = self.controller.ScanAddresses(self.min_add, self.max_add)
       
       logger.info(f'Connected to Elliptec device at {com_port}')
       i = 0
       
       for device in elliptec: 
           if self.controller.Configure(device): 
                self.elliptec_list.append(self.controller.AddressedDevice(device[0]))  
                # self.elliptec_list = self.controller.AddressedDevice(device[0])
                self.device_address.append(self.convert_to_char(self.elliptec_list[i].Address))
                self.device_info.append(self.elliptec_list[i].DeviceInfo)
                
                for stri in self.device_info[i].Description():
                    units = self.extract_units(stri)
                    self.units.append(units)
                    print(stri)
                i += 1

    def convert_to_char(self, address): 
        char_list = List[Char]()
        char_list.Add(Char.Parse(address))
        return char_list
    
    def extract_units(self, device_info): 
        for line in device_info:
            if 'mm' in line: 
                return 'mm'
            elif 'deg' in line:
                return 'deg'
            else: 
                return 'unknown'

    #ELLBaseDevice or ELLDevices? 
    def move_abs(self, actuator, value): 
        """
        actuator: index integer of the actuator to move
        """
        boolean = self.elliptec_list[actuator-1].MoveAbsolute(self.device_address[actuator-1], Decimal(value)) # DK - I think the first attribute should be '1'/'2' or 1/2 because this is supposed to be 'address' in the documentation. 
        return boolean
    
    def move_rel(self, actuator, value): 
        boolean = self.elliptec_list[actuator-1].MoveRelative(self.device_address[actuator-1], Decimal(value))
        return boolean
    
    def home(self, actuator): 
        if "LinearStage" in self.get_device_type(actuator):
            boolean = self.elliptec_list[actuator-1].Home(self.device_address[actuator-1], ELLBaseDevice.DeviceDirection.Linear)
            return boolean
        elif "OpticsRotator" in self.get_device_type(actuator):
            boolean = self.elliptec_list[actuator-1].Home(self.device_address[actuator-1], ELLBaseDevice.DeviceDirection.Clockwise)
            return boolean
        else:
            logger.error(f'Unknown device type: {self.get_device_type(actuator)}')

    def get_position(self, actuator): 
        logger.info(f'Current position: {self.elliptec_list[actuator-1].GetPosition()}')
        return float(str(self.elliptec_list[actuator-1].get_Position()))

    def get_device_type(self, actuator): 
        """Get the device type of the connected device"""
        return str(self.device_info[actuator-1].get_DeviceType())

    def get_units(self, actuator): 
       return self.device_info[actuator-1].Units
    def close(self): 
        ELLDevicePort.Disconnect()
        logger.info('Disconnected from Elliptec device')