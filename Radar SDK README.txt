==============================================================================
Python Wrapper for Radar SDK
==============================================================================

Description:
------------

The python wrapper makes radar SDK available from Python.

The Python wrapper works with Python 3.6 or higher on Windows (x86, x64) and
Linux (x64, Raspberry Pi).

The wrapper depends on the compiled radar SDK library (radar_sdk.dll on
Windows, libradar_sdk.so on Linux). The wrapper tries to first find the file
in the directory of the wrapper (the directory that contains ifxRadarSDK.py).
If not found, the library is searched in the directory ../../lib/ARCH/ where
ARCH is depending on the platform one of win32_x86, win32_x64, raspi,
linux_x64.

Note: your python installation might be either 64-bit or 32-bit and radar_sdk.dll
must be built to match it. Following error message indicates such a mismatch:
"OSError: [WinError 193] %1 is not a valid Win32 application".
Also, just as for the radar_sdk library which should be reachable throught the system
path or by making it available (by copy) in the wrapper directory the same should be
done for the system runtime libraries (especially when the MINGW toolchain is used).

API and documentation
---------------------

Create functions of the radar SDK correspond to constructors of classes.
destroy functions are implicitly called by the corresponding destructors. C
structs are mapped to dictionaries. All SDK error codes are mapped to a Python
exception.

A full documentation is available as docstrings. You can access the
documentation within python via:
>>> import ifxRadarSDK
>>> help(ifxRadarSDK)

Example:
--------

The file example.py contains a simple example code which illustrates how to
use the wrapper to connect to a radar device and read data from it.
