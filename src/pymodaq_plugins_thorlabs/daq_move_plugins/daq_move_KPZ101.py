from pymodaq.control_modules.move_utility_classes import DAQ_Move_base, main, comon_parameters_fun, DataActuatorType, \
    DataActuator
from pymodaq.utils.daq_utils import ThreadCommand

from pymodaq.utils.parameter import Parameter
from pymodaq.utils.logger import set_logger, get_module_name

from pymodaq_plugins_thorlabs.hardware.kinesis import serialnumbers_piezo, Piezo

logger = set_logger(get_module_name(__file__))


class DAQ_Move_KPZ101(DAQ_Move_base):
    """
    Wrapper object to access Piezo functionalities, similar to Kinesis instruments 
    """
    _controller_units = Piezo.default_units
    is_multiaxes = True
    _axis_names = ['X-axis']
    _epsilon = 0.01
    data_actuator_type = DataActuatorType.DataActuator
    params = [{'title': 'Controller ID:', 'name': 'controller_id', 'type': 'str', 'value': '', 'readonly': True},
              {'title': 'Serial Number:', 'name': 'serial_number', 'type': 'list',
               'limits': serialnumbers_piezo, 'value': serialnumbers_piezo[0]}
              # {'title': 'Serial number:', 'name': 'serial_number', 'type': 'list',
              #  'limits': serialnumbers_piezo[0]},
              ] + comon_parameters_fun(is_multiaxes, axis_names=_axis_names, epsilon=_epsilon)

    def ini_attributes(self):
        self.controller: Piezo = None
        self._move_done = False
        # try:
        #     self.controller: Piezo = None
        #     self.settings.child('bounds', 'is_bounds').setValue(True)
        #     self.settings.child('bounds', 'max_bound').setValue(360)
        #     self.settings.child('bounds', 'min_bound').setValue(0)
        # except Exception as e:
        #     logger.exception(str(e) + ' in DAQ_Move_KPZ101.ini_attributes')

    def commit_settings(self, param: Parameter):
        """Apply the consequences of a change of value in the detector settings

        Parameters
        ----------
        param: Parameter
            A given parameter (within detector_settings) whose value has been changed by the user
        """
        if param.name() == 'axis':
            self.axis_unit = self.controller.get_units(self.axis_value)
            # update the units are they are not known before hand in the driver class but only
            # after initialization of the controller

    def ini_stage(self, controller=None):
        """Actuator communication initialization

        Parameters
        ----------
        controller: (object)
            custom object of a PyMoDAQ plugin (Slave case). None if only one actuator by controller (Master case)

        Returns
        -------
        info: str
        initialized: bool
            False if initialization failed otherwise True
        """

        if self.is_master:
            self.controller = Piezo()
            self.controller.connect(self.settings['serial_number'])
        else:
            self.controller = controller

        # update the axis unit by interogating the controller and the specific axis
        self.axis_unit = self.controller.get_units(self.axis_value)

        if not self.controller.is_homed(self.axis_value):
            self.move_home()

        info = f'{self.controller.name} - {self.controller.serial_number}'
        initialized = True
        return info, initialized

        # """
        # Connect to Kinesis Piezo Stage by communicating with kinesis.py
        # """
        # self.controller = self.ini_stage_init(controller, Piezo())
        #
        # try:
        #     self.controller.connect(self.settings.child('serial_number').value())
        # except Exception as e:
        #     logger.exception(str(e) + ' in DAQ_Move_KPZ101.ini_stage')
        #
        # # if self.settings['multiaxes', 'multi_status'] == "Master":
        # #     self.controller.connect(self.settings(['serial_number']))
        # try:
        #     info = self.controller.name
        #     self.settings.child('controller_id').setValue(info)
        # except Exception as e:
        #     logger.exception(str(e) + ' in DAQ_Move_KPZ101.ini_stage')
        # # info = self.controller.name
        # # self.settings.child('controller_id').setValue(info)
        # try:
        #     initialized = True
        # except Exception as e:
        #     logger.exception(str(e) + ' in DAQ_Move_KPZ101.ini_stage')
        #     initialized = False
        # # initialized = True
        # return info, initialized

    def close(self):
        """
            close the current instance of Kinesis instrument.
        """
        if self.controller is not None:
            self.controller.close()

    def stop_motion(self):
        """
            See Also
            --------
            DAQ_Move_base.move_done
        """
        if self.controller is not None:
            self.controller.stop()

    def user_condition_to_reach_target(self) -> bool:
        """ Implement a condition for exiting the polling mechanism and specifying that the
        target value has been reached

       Returns
        -------
        bool: if True, PyMoDAQ considers the target value has been reached
        """

        return self._move_done

    # def get_actuator_value(self):
    #     """
    #         Get the current hardware position with scaling conversion of the Kinsesis instrument provided by get_position_with_scaling
    #
    #         See Also
    #         --------
    #         DAQ_Move_base.get_position_with_scaling, daq_utils.ThreadCommand
    #     """
    #
    #     # pos = self.controller.get_position()
    #     # pos = self.get_position_with_scaling(pos)
    #     pos = DataActuator(
    #         data=self.controller.get_position(),
    #         units=self.controller.get_units(),
    #     )
    #     pos = self.get_position_with_scaling(pos)
    #     return pos

    def get_actuator_value(self):
        """Get the current value from the hardware with scaling conversion.

        Returns
        -------
        float: The position obtained after scaling conversion.
        """
        pos = DataActuator(
            data=self.controller.get_position(self.axis_value),
            units=self.controller.get_units(self.axis_value)
        )
        pos = self.get_position_with_scaling(pos)
        return pos

    def move_abs(self, value: DataActuator):
        """ Move the actuator to the absolute target defined by value

        Parameters
        ----------
        value: (float) value of the absolute target positioning
        """
        self._move_done = False
        value = self.check_bound(value)
        self.target_value = value
        value = self.set_position_with_scaling(value)  # apply scaling if the user specified one
        self.controller.move_abs(value.value(), channel=self.axis_value)

    def move_rel(self, value: DataActuator):
        """ Move the actuator to the relative target actuator value defined by value

        Parameters
        ----------
        value: (float) value of the relative target positioning
        """
        self._move_done = False
        value = self.check_bound(self.current_position + value) - self.current_position
        self.target_value = value + self.current_position
        value = self.set_position_relative_with_scaling(value)
        self.controller.move_abs(self.target_value.value())

    def move_home(self):
        """
        Move the Kinesis Piezo Stage to home position
        """
        self._move_done = False
        self.controller.home(callback=self.move_done_callback)


if __name__ == '__main__':
    main(__file__, init=False)
