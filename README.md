# MCP4725 12-bit Single Channel DAC

The MCP4725 is a 12-bit, single channel Digital-to-Analog (DAC) converter.  It runs on I2C and typically has two address options set by the A0 pin and a factory set A1 and A2 values.

## Python code for the Raspberry Pi
This is a very basic program to allow you to use the MCP4725 with a Raspberry Pi. It does not have any special features, but can easily be modified to include them.  It was tested on Python 3.10, but should easily work with later versions of Python.

## SMBus
This program uses smbus.  Any recent version is likely to work as only basic functions are used.

This project is licensed under the terms of the MIT license.
