#!/usr/bin/env python3

import MCP4725 as MCP

mcp = MCP.MCP4725() # ref_voltage = 5. and address = 0x62
mcp.general_call_reset() # Ensure the powerdown mode is normal

mcp.set_dac_voltage(2.1) # Sets DAC, not EEPROM
mcp.set_dac_voltage_eeprom(3.7) # Sets DAC, and EEPROM
mcp.fast_write_DAC_voltages(3.1) # Sets DAC, not EEPROM

print(f"DAC Voltage: {mcp.get_dac_voltage()}")
print(f"EEPROM Voltage: {mcp.get_eeprom_voltage()}") #Should be different than dac voltage

#Should both return [0,0] i.e. Normal Mode
print(mcp.get_dac_pd_mode())
print(mcp.get_eeprom_pd_mode())

