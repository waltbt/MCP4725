#!/usr/bin/env python3

"""
MCP4725.py
Function: A simple class to operate an MCP4725 DAC on an RPi with Python
Author: Benjamin Walt
Date: 10/27/2022
Version: 0.1
Copyright (c) Benjamin Thomas Walt
Licensed under the MIT license.
"""


import smbus
import time


class MCP4725:

	def __init__(self, ref_voltage=5., address = 0x62): # Default address depends on supplier 0x62 is adafruit, 0x60 is sparkfun
		self._bus = smbus.SMBus(1) # Channel = 1
		self._address = address
		self._reference_voltage = ref_voltage
		self._cur_voltage = 0.0
		self.set_dac_voltage_eeprom(0.0) # Ensure the voltage is zero on start up

	def _write_reg(self, value):
		"""Write a block of data, no registers are used"""
		self._bus.write_i2c_block_data(self._address, value[0], value[1:]) # First entry takes place of register
	
	def _read_reg(self, length):
		"""Read a block of data, no registers are used"""
		return self._bus.read_i2c_block_data(self._address, 0, length) #No registers, so 0 is offset

	"""
	See section 6.1.1
	"""
	def fast_write_DAC_voltages(self, voltage):
		"""Alternate write command that does not write to EEPROM"""
		digital_val = int((voltage/self._reference_voltage)*4095) # Create an int value between 0 and 4095
		digital_val = max(0, min(4095, digital_val))

		# Set up values to write based on desired voltage
		upper = (digital_val & 0xf00) >> 8 # Upper bits (0|0|0|0|D11|D10|D9|D8) PD1 and PD0 = 0
		lower = (digital_val & 0xff) # Lower bits (D7|D6|D5|D4|D3|D2|D1|D0)
		msg = [upper, lower]
		self._write_reg(msg)
		self._cur_voltage = voltage

	"""
	See section 6.1.2
	"""
	def set_dac_voltage(self, voltage):
		"""Write command to change DAC values - NOT EEPROM"""
		digital_val = int((voltage/self._reference_voltage)*4095) # Create an int value btween 0 and 4095
		digital_val = max(0, min(4095, digital_val))

		# Set up values to write based on desired voltage
		command = 0x40 # (C2=0|C1=1|C0=0|X|X|PD1=0|PD0=0|X)
		upper = (digital_val & 0xff0) >> 4 # Upper bits (D11|D10|D9|D8|D7|D6|D5|D4)
		lower = (digital_val & 0xf) << 4 # Lower bits (D3|D2|D1|D0|X|X|X|X)
		msg = [command, upper, lower]
		self._write_reg(msg)
		self._cur_voltage = voltage

	"""
	See section 6.1.2
	There are a limited number of write cycles to the EEPROM, so it is best to use another method for routine write.
	It is rated for >1,000,000 cycles.
	"""
	def set_dac_voltage_eeprom(self, voltage):
		"""Write command to change DAC values and EEPROM."""
		digital_val = int((voltage/self._reference_voltage)*4095) # Create an int value between 0 and 4095
		digital_val = max(0, min(4095, digital_val))

		# Set up values to write based on desired voltage
		command = 0x60 # (C2=0|C1=1|C0=1|X|X|PD1=0|PD0=0|X)
		upper = (digital_val & 0xff0) >> 4 # Upper bits (D11|D10|D9|D8|D7|D6|D5|D4)
		lower = (digital_val & 0xf) << 4 # Lower bits (D3|D2|D1|D0|X|X|X|X)
		msg = [command, upper, lower]
		self._write_reg(msg)
		self._cur_voltage = voltage
		while(not self.get_rdy_bsy()): # Need time to finish write to EEPROM
			time.sleep(0.05) 


	def get_dac_voltage(self):
		"""Returns the voltage stored in the DAC registers"""
		data = self._read_reg(3)
		top = data[1] << 4
		bottom = data[2] >> 4
		return self._reference_voltage*((top + bottom)/4095.)
	
	def get_dac_pd_mode(self):
		"""Returns the power down values stored in the DAC registers"""
		data = self._read_reg(3)
		pd0 = (data[0] >> 1) & 1
		pd1 = (data[0] >> 2) & 1
		return [pd0, pd1]
		
	
	def get_eeprom_voltage(self):
		"""Returns the voltage stored in the EEPROM registers"""
		data = self._read_reg(5)
		top = (data[3] & 0x0f) << 8
		bottom = data[4]
		return self._reference_voltage*((top + bottom)/4095.)
	
	def get_eeprom_pd_mode(self):
		"""Returns the power down values stored in the EEPROM registers"""
		data = self._read_reg(5)
		pd0 = (data[3] >> 5) & 1
		pd1 = (data[3] >> 6) & 1
		return [pd0, pd1]
	
	def get_rdy_bsy(self):
		"""Returns the value of the rdy/bsy register.  Indicates that the EEPROM is being written"""
		"""
		0 - Busy
		1 - Ready
		"""
		data = self._read_reg(1)
		return (data[0] >> 7) & 1
	
	"""
	Aborts current conversion
	Internal reset
	After reset, EEPROM values loaded into DAC
	"""
	def general_call_reset(self):
		"""General Call Reset"""
		self._bus.write_byte(0, 0x06)
	
	"""
	Resets power down bits to Normal Mode 0,0 in the DAC
	"""
	def general_call_wake_up(self):
		"""General Call Wake-Up"""
		self._bus.write_byte(0, 0x09)
	
