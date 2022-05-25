# ===========================================================================
# Copyright (C) 2021 Infineon Technologies AG
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ===========================================================================

"""Python wrapper for Infineon Radar SDK

The package expects the library (radar_sdk.dll on Windows, libradar_sdk.so on
Linux) either in the same directory as this file (ifxRadarSDK.py) or in a
subdirectory ../../libs/ARCH/ relative to this file where ARCH is depending on
the platform either win32_x86, win32_x64, raspi, or linux_x64.
"""

# Add the current directory to the sys.path if it is not already added. Not very pythonic,
# but an acceptable solution.
import sys
from pathlib import Path
from enum import IntEnum

_cur_dir = str(Path(__file__).parent)
if _cur_dir not in sys.path:
    sys.path.append(_cur_dir)

from ctypes import *
import platform, os, sys
import numpy as np
from ifxError import *

# by default,
#   from ifxRadarSDK import *
# would import all objects, including the ones from ctypes. To avoid name space
# pollution, we list what symbols should be exported.
__all__ = ["Frame", "Device", "GeneralError",
           "get_version", "get_version_full", "ShieldType"]

def find_library():
    """Find path to dll/shared object"""
    system = None
    libname = None
    if platform.system() == "Windows":
        libname = "radar_sdk.dll"
        is64bit = bool(sys.maxsize > 2**32)
        if is64bit:
            system = "win32_x64"
        else:
            system = "win32_x86"
    elif platform.system() == "Linux":
        libname = "libradar_sdk.so"
        machine = os.uname()[4]
        if machine == "x86_64":
            system = "linux_x64"
        elif machine == "armv7l":
            system = "raspi"
        elif machine == "aarch64":
            system = "linux_aarch64"

    if system == None or libname == None:
        raise RuntimeError("System not supported")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    for reldir in (".", os.path.join("../../../libs/", system)):
        libpath = os.path.join(script_dir, reldir, libname)
        if os.path.isfile(libpath):
            return libpath

    raise RuntimeError("Cannot find " + libname)

# types
class ShieldType(IntEnum):
    Missing            = 0x0000
    Unknown            = 0x0001
    RBBMCU7            = 0x0100
    BGT60TR13AIP       = 0x0200
    BGT60ATR24AIP      = 0x0201
    BGT60UTR11         = 0x0202
    BGT60UTR13D        = 0x0203
    BGT60LTR11         = 0x0300
    BGT60LTR11MONOSTAT = 0x0301
    BGT60LTR11B11      = 0x302
    BGT24ATR22ES       = 0x400
    BGT24ATR22PROD     = 0x401
    Any                = 0xFFFF

# structs
class DeviceConfigStruct(Structure):
    """Wrapper for structure ifx_Device_Config_t"""
    _fields_ = (("sample_rate_Hz", c_uint32),
                ("rx_mask", c_uint32),
                ("tx_mask", c_uint32),
                ("tx_power_level", c_uint32),
                ("if_gain_dB", c_uint32),
                ("lower_frequency_Hz", c_uint64),
                ("upper_frequency_Hz", c_uint64),
                ("num_samples_per_chirp", c_uint32),
                ("num_chirps_per_frame", c_uint32),
                ("chirp_repetition_time_s", c_float),
                ("frame_repetition_time_s", c_float),
                ("mimo_mode", c_int))

class DeviceMetricsStruct(Structure):
    """Wrapper for structure ifx_Device_Metrics_t"""
    _fields_ = (("sample_rate_Hz", c_uint32),
                ("rx_mask", c_uint32),
                ("tx_mask", c_uint32),
                ("tx_power_level", c_uint32),
                ("if_gain_dB", c_uint32),
                ("range_resolution_m", c_float),
                ("max_range_m", c_float),
                ("max_speed_m_s", c_float),
                ("speed_resolution_m_s", c_float),
                ("frame_repetition_time_s", c_float),
                ("center_frequency_Hz", c_float))

class DeviceListEntry(Structure):
    """Wrapper for structure ifx_Device_Config_t"""
    _fields_ = (("board_type", c_int),
                ("shield_uuid", c_char*64))


class MatrixRStruct(Structure):
    _fields_ = (('d', POINTER(c_float)),
                ('rows', c_uint32),
                ('cols', c_uint32),
                ('lda', c_uint32, 31),
                ('owns_d', c_uint8, 1))

class FrameStruct(Structure):
    _fields_ = (('num_rx', c_uint8),
                ('rx_data', POINTER(POINTER(MatrixRStruct))))
                
class DeviceInfoStruct(Structure):
    _fields_ = (('description', c_char_p),
                ('min_rf_frequency_Hz', c_uint64),
                ('max_rf_frequency_Hz', c_uint64),
                ('num_tx_antennas', c_uint8),
                ('num_rx_antennas', c_uint8),
                ('max_tx_power', c_uint8),
                ('num_temp_sensors', c_uint8),
                ('interleaved_rx', c_uint8),
                ('shield_type', c_uint32))


class DeviceMetricsStruct(Structure):
    _fields_ = (('sample_rate_Hz', c_uint32),
                ('rx_mask', c_uint32),
                ('tx_mask', c_uint32),
                ('tx_power_level', c_uint32),
                ('if_gain_dB', c_uint32),
                ('range_resolution_m', c_float),
                ('max_range_m', c_float),
                ('max_speed_m_s', c_float),
                ('speed_resolution_m_s', c_float),
                ('frame_repetition_time_s', c_float),
                ('center_frequency_Hz', c_float))


class FirmwareInfoStruct(Structure):
    _fields_ = (('description', c_char_p),
                ('version_major', c_uint16),
                ('version_minor', c_uint16),
                ('version_build', c_uint16),
                ('extended_version', c_char_p))

FrameStructPointer = POINTER(FrameStruct)
MatrixRStructPointer = POINTER(MatrixRStruct)
DeviceConfigStructPointer = POINTER(DeviceConfigStruct)
DeviceMetricsStructPointer = POINTER(DeviceMetricsStruct)
FirmwareInfoPointer = POINTER(FirmwareInfoStruct)
DeviceInfoPointer = POINTER(DeviceInfoStruct)

def initialize_module():
    """Initialize the module and return ctypes handle"""
    dll = CDLL(find_library())

    dll.ifx_sdk_get_version_string.restype = c_char_p
    dll.ifx_sdk_get_version_string.argtypes = None

    dll.ifx_sdk_get_version_string_full.restype = c_char_p
    dll.ifx_sdk_get_version_string_full.argtypes = None

    # error
    dll.ifx_error_to_string.restype = c_char_p
    dll.ifx_error_to_string.argtypes = [c_int]

    dll.ifx_error_get_and_clear.restype = c_int
    dll.ifx_error_get_and_clear.argtypes = None

    # device
    dll.ifx_device_create.restype = c_void_p
    dll.ifx_device_create.argtypes = None

    dll.ifx_device_register_list_string.restype = POINTER(c_char)
    dll.ifx_device_register_list_string.argtypes = [c_void_p, c_bool]

    dll.ifx_mem_free.restype = None
    dll.ifx_mem_free.argtypes = [c_void_p]

    dll.ifx_device_create_by_port.restype = c_void_p
    dll.ifx_device_create_by_port.argtypes = [c_char_p]

    dll.ifx_device_get_list.restype = c_void_p
    dll.ifx_device_get_list.argtypes = None

    dll.ifx_device_get_list_by_shield_type.restype = c_void_p
    dll.ifx_device_get_list_by_shield_type.argtypes = [c_int]

    dll.ifx_device_create_by_uuid.restype = c_void_p
    dll.ifx_device_create_by_uuid.argtypes = [c_char_p]

    dll.ifx_device_get_shield_uuid.restype = c_char_p
    dll.ifx_device_get_shield_uuid.argtypes = [c_void_p]

    dll.ifx_device_set_config.restype = None
    dll.ifx_device_set_config.argtypes = [c_void_p, DeviceConfigStructPointer]

    dll.ifx_device_get_config.restype = None
    dll.ifx_device_get_config.argtypes = [c_void_p, DeviceConfigStructPointer]

    dll.ifx_device_get_config_defaults.restype = None
    dll.ifx_device_get_config_defaults.argtypes = [c_void_p, DeviceConfigStructPointer]

    dll.ifx_device_get_metrics_defaults.restype = None
    dll.ifx_device_get_metrics_defaults.argtypes = [c_void_p, DeviceMetricsStructPointer]

    dll.ifx_device_start_acquisition.restype = c_bool
    dll.ifx_device_start_acquisition.argtypes = [c_void_p]

    dll.ifx_device_stop_acquisition.restype = c_bool
    dll.ifx_device_stop_acquisition.argtypes = [c_void_p]

    dll.ifx_device_destroy.restype = None
    dll.ifx_device_destroy.argtypes = [c_void_p]

    dll.ifx_device_create_frame_from_device_handle.restype = FrameStructPointer
    dll.ifx_device_create_frame_from_device_handle.argtypes = [c_void_p]

    dll.ifx_device_get_next_frame.restype = c_int
    dll.ifx_device_get_next_frame.argtypes = [c_void_p , FrameStructPointer]

    dll.ifx_device_get_next_frame_timeout.restype = c_int
    dll.ifx_device_get_next_frame_timeout.argtypes = [c_void_p , FrameStructPointer, c_uint16]

    dll.ifx_device_get_temperature.restype = None
    dll.ifx_device_get_temperature.argtypes = [c_void_p , POINTER(c_float)]
    
    dll.ifx_device_get_firmware_information.restype = FirmwareInfoPointer
    dll.ifx_device_get_firmware_information.argtypes = [c_void_p]

    dll.ifx_device_get_device_information.restype = DeviceInfoPointer
    dll.ifx_device_get_device_information.argtypes = [c_void_p] 

    dll.ifx_device_translate_metrics_to_config.restype = c_void_p
    dll.ifx_device_translate_metrics_to_config.argtypes = [c_void_p, DeviceMetricsStructPointer, DeviceConfigStructPointer]

    # frame
    dll.ifx_frame_create_r.restype = FrameStructPointer
    dll.ifx_frame_create_r.argtypes = [c_uint8, c_uint32, c_uint32]

    dll.ifx_frame_destroy_r.restype = None
    dll.ifx_frame_destroy_r.argtypes = [FrameStructPointer]

    dll.ifx_frame_get_mat_from_antenna_r.restype = MatrixRStructPointer
    dll.ifx_frame_get_mat_from_antenna_r.argtypes = [FrameStructPointer, c_uint8]

    # list
    dll.ifx_list_destroy.restype = None
    dll.ifx_list_destroy.argtypes = [c_void_p]

    dll.ifx_list_size.restype = c_size_t
    dll.ifx_list_size.argtypes = [c_void_p]

    dll.ifx_list_get.restype = c_void_p
    dll.ifx_list_get.argtypes = [c_void_p, c_size_t]

    # export the error class
    for actual_error_class in error_class_list:
        __all__.append(actual_error_class)

    return dll

dll = initialize_module()

def get_version():
    """Return SDK version string (excluding git tag from which it was build)"""
    return dll.ifx_sdk_get_version_string().decode("ascii")

def get_version_full():
    """Return full SDK version string including git tag from which it was build"""
    return dll.ifx_sdk_get_version_string_full().decode("ascii")

def check_rc(error_code=None):
    """Raise an exception if error_code is not IFX_OK (0)"""
    if error_code == None:
        error_code = dll.ifx_error_get_and_clear()

    if error_code:
        raise_exception_for_error_code(error_code, dll)

class Frame():
    def __init__(self, num_antennas, num_chirps_per_frame, num_samples_per_chirp):
        """Create frame for time domain data acquisition

        This function initializes a data structure that can hold a time domain
        data frame according to the dimensions provided as parameters.

        If a device is connected then the method Device.create_frame_from_device_handle
        can be used instead of this function, as that function reads the
        dimensions from configured the device handle.

        Parameters:
            num_antennas            Number of virtual active Rx antennas configured in the device
            num_chirps_per_frame    Number of chirps configured in a frame
            num_samples_per_chirp   Number of chirps configured in a frame
        """
        self.handle = dll.ifx_frame_create_r(num_antennas, num_chirps_per_frame, num_samples_per_chirp)
        check_rc()

    @classmethod
    def create_from_pointer(cls, framepointer):
        """Create Frame from FramePointer"""
        self = cls.__new__(cls)
        self.handle = framepointer
        return self

    def __del__(self):
        """Destroy frame handle"""
        if hasattr(self, "handle"):
            dll.ifx_frame_destroy_r(self.handle)

    def get_num_rx(self):
        """Return the number of virtual active Rx antennas in the radar device"""
        return self.handle.contents.num_rx

    def get_mat_from_antenna(self, antenna, copy=True):
        """Get matrix from antenna

        If copy is True, a copy of the original matrix is returned. If copy is
        False, the matrix is not copied and the matrix must *not* be used after
        the frame object has been destroyed.

        Parameters:
            antenna     number of antenna
            copy        if True a copy of the matrix will be returned
        """
        # we don't have to free mat because the matrix is saved in the frame
        # handle.
        # matrices are in C order (row major order)
        mat = dll.ifx_frame_get_mat_from_antenna_r(self.handle, antenna)
        d = mat.contents.d
        shape = (mat.contents.rows, mat.contents.cols)
        return np.array(np.ctypeslib.as_array(d, shape), order="C", copy=copy)


class Device():
    @staticmethod
    def get_list(shield_type=ShieldType.Any):
        """Return a list of com ports

        The function returns a list of unique ids (uuids) that correspond to
        radar devices. The Shield type can be optionally specified.

        **Examples**
            for uuid in Device.get_list(): #scans all types of radar devices
                dev = Device(uuid)
                # ...
			for uuid in Device.get_list(ShieldType.BGT60TR13AIP): #scans all devices with specified shield attached

        Parameters:
            shield_type     Shield type of type ShieldType
        """
        uuids = []

        ifx_list = dll.ifx_device_get_list_by_shield_type(int(shield_type))
        size = dll.ifx_list_size(ifx_list)
        for i in range(size):
            p = dll.ifx_list_get(ifx_list, i)
            entry = cast(p, POINTER(DeviceListEntry))
            uuids.append(entry.contents.shield_uuid.decode("ascii"))
        dll.ifx_list_destroy(ifx_list)

        return uuids

    def __init__(self, uuid=None, port=None):
        """Create new device

        Search for a Infineon radar sensor device connected to the host machine
        and connects to the first found sensor device.

        The device is automatically closed by the destructor. If you want to
        close the device yourself, you can use the keyword del:
            device = Device()
            # do something with device
            ...
            # close device
            del device

        If port is given, the specific port is opened. If uuid is given and
        port is not given, the radar device with the given uuid is opened. If
        no parameters are given, the first found radar device will be opened.

        Examples:
          - Open first found radar device:
            dev = Device()
          - Open radar device on COM5:
            dev = Device(port="COM5")
          - Open radar device with uuid 0123456789abcdef0123456789abcdef
            dev = Device(uuid="0123456789abcdef0123456789abcdef")

        Optional parameters:
            port:       opens the given port
            uuid:       open the radar device with unique id given by uuid
                        the uuid is represented as a 32 character string of
                        hexadecimal characters. In addition, the uuid may
                        contain dash characters (-) which will be ignored.
                        Both examples are valid and correspond to the same
                        uuid:
                            0123456789abcdef0123456789abcdef
                            01234567-89ab-cdef-0123-456789abcdef
        """
        h = None
        if uuid:
            h = dll.ifx_device_create_by_uuid(uuid.encode("ascii"))
        elif port:
            h = dll.ifx_device_create_by_port(port.encode("ascii"))
        else:
            h = dll.ifx_device_create()
        
        self.handle = c_void_p(h) # Reason of that cast HMI-2896

        # check return code
        check_rc()
        
    def _mimo_c_val_2_str(mimo_int):
         if(mimo_int == 0):
             return "off"
         elif(mimo_int == 1):
             return "tdm"
         else:
             raise ValueError("Wrong mimo_mode")
    
    def translate_metrics_to_config(
                self,
                sample_rate_Hz=1000000,
                range_resolution_m=0.150,
                max_range_m=9.59,
                max_speed_m_s=2.45,
                speed_resolution_m_s=0.08,
                frame_repetition_time_s=1/10,
                center_frequency_Hz=60750000000,
                rx_mask=7,
                tx_mask=1,
                tx_power_level=31,
                if_gain_dB=33):
        """Derives a device configuration from specified feature space metrics.

        This functions calculates FMCW frequency range, number of samples per chirp, number of chirps
        per frame and chirp-to-chirp time needed to achieve the specified feature space metrics. Number
        of samples per chirp and number of chirps per frame are rounded up to the next power of two,
        because this is a usual constraint for range and Doppler transform. The resulting maximum range
        and maximum speed may therefore be larger than specified.

        Configuration is returned as dictionary that can be used for setting
        config of device. Values are same as input parameters of self.se
        
        Parameters:
            sample_rate_Hz:
                Sampling rate of the ADC used to acquire the samples during a
                chirp. The duration of a single chirp depends on the number of
                samples and the sampling rate.

            range_resolution_m:
                The range resolution is the distance between two consecutive
                bins of the range transform. Note that even though zero
                padding before the range transform seems to increase this
                resolution, the true resolution does not change but depends
                only from the acquisition parameters. Zero padding is just
                interpolation!

            max_range_m:
                The bins of the Doppler transform represent the speed values
                between -max_speed_m_s and max_speed_m_s.

            max_speed_m_s:
                The bins of the Doppler transform represent the speed values
                between -max_speed_m_s and max_speed_m_s.

            
            speed_resolution_m_s:
                The speed resolution is the distance between two consecutive
                bins of the Doppler transform. Note that even though zero
                padding before the speed transform seems to increase this
                resolution, the true resolution does not change but depends
                only from the acquisition parameters. Zero padding is just
                interpolation!

            frame_repetition_time_s:
                The desired frame repetition time in seconds (also known
                as frame time or frame period). The frame repetition time
                is the inverse of the frame rate

            center_frequency_Hz:
                Center frequency of the FMCW chirp. If the value is set to 0
                the center frequency will be determined from the device

            rx_mask:
                Bitmask where each bit represents one RX antenna of the radar
                device. If a bit is set the according RX antenna is enabled
                during the chirps and the signal received through that antenna
                is captured. The least significant bit corresponds to antenna
                1.

            tx_mask:
                Bitmask where each bit represents one TX antenna. Analogous to
                rx_mask.
          
            tx_power_level:
                This value controls the power of the transmitted RX signal.
                This is an abstract value between 0 and 31 without any physical
                meaning.

            if_gain_dB:
                Amplification factor that is applied to the IF signal coming
                from the RF mixer before it is fed into the ADC.
        """
        
        m = DeviceMetricsStruct()
        m.sample_rate_Hz = sample_rate_Hz
        m.range_resolution_m = range_resolution_m
        m.max_range_m = max_range_m
        m.max_speed_m_s = max_speed_m_s
        m.speed_resolution_m_s = speed_resolution_m_s
        m.frame_repetition_time_s = frame_repetition_time_s
        m.center_frequency_Hz = center_frequency_Hz
        
        m.rx_mask = rx_mask
        m.tx_mask = tx_mask
        m.tx_power_level = tx_power_level
        m.if_gain_dB = if_gain_dB
        
        config = DeviceConfigStruct()

        dll.ifx_device_translate_metrics_to_config(self.handle, byref(m), byref(config))
        c_dict = dict()
        for field in config._fields_:
            name = field[0]
            c_dict[name] = getattr(config, name)
        c_dict["mimo_mode"] = Device._mimo_c_val_2_str(c_dict["mimo_mode"])
        return c_dict

    def set_config(self,
               sample_rate_Hz = 1e6,
               rx_mask = 1,
               tx_mask = 1,
               tx_power_level = 31,
               if_gain_dB = 33,
               lower_frequency_Hz = 58e9,
               upper_frequency_Hz = 63e9,
               num_samples_per_chirp = 128,
               num_chirps_per_frame = 32,
               chirp_repetition_time_s = 5e-4,
               frame_repetition_time_s = 0.1,
               mimo_mode = "off"):
        """Configure device and start acquisition of time domain data

        The board is configured according to the parameters provided
        through config and acquisition of time domain data is started.

        Parameters:
            sample_rate_Hz:
                Sampling rate of the ADC used to acquire the samples during a
                chirp. The duration of a single chirp depends on the number of
                samples and the sampling rate.

            rx_mask:
                Bitmask where each bit represents one RX antenna of the radar
                device. If a bit is set the according RX antenna is enabled
                during the chirps and the signal received through that antenna
                is captured. The least significant bit corresponds to antenna
                1.

            tx_mask:
                Bitmask where each bit represents one TX antenna. Analogous to
                rx_mask.

            tx_power_level:
                This value controls the power of the transmitted RX signal.
                This is an abstract value between 0 and 31 without any physical
                meaning.

            if_gain_dB:
                Amplification factor that is applied to the IF signal coming
                from the RF mixer before it is fed into the ADC.

            lower_frequency_Hz:
                Lower frequency (start frequency) of the FMCW chirp.

            upper_frequency_Hz:
                Upper frequency (stop frequency) of the FMCW chirp.

            num_samples_per_chirp:
                This is the number of samples acquired during each chirp of a
                frame. The duration of a single chirp depends on the number of
                samples and the sampling rate.

            num_chirps_per_frame:
                This is the number of chirps a single data frame consists of.

            chirp_repetition_time_s:
                This is the time period that elapses between the beginnings of
                two consecutive chirps in a frame. (Also commonly referred to as
                pulse repetition time or chirp-to-chirp time.)

            frame_repetition_time_s:
                This is the time period that elapses between the beginnings of
                two consecutive frames. The reciprocal of this parameter is the
                frame rate. (Also commonly referred to as frame time or frame
                period.)

            mimo_mode:
                Mode of MIMO. Allowed values are "tdm" for
                time-domain-multiplexed MIMO or "off" for MIMO deactivated.
        """
        if mimo_mode.lower() == "tdm":
            mimo_mode = 1
        else:
            mimo_mode = 0

        config = DeviceConfigStruct(int(sample_rate_Hz),
                                    rx_mask,
                                    tx_mask,
                                    tx_power_level,
                                    if_gain_dB,
                                    int(lower_frequency_Hz),
                                    int(upper_frequency_Hz),
                                    num_samples_per_chirp,
                                    num_chirps_per_frame,
                                    chirp_repetition_time_s,
                                    frame_repetition_time_s,
                                    mimo_mode)
        dll.ifx_device_set_config(self.handle, byref(config))
        check_rc()

    def get_config(self):
        """Get the configuration from the device"""
        config = DeviceConfigStruct()
        dll.ifx_device_get_config(self.handle, byref(config))
        check_rc()
        # return struct as dictionary
        return dict((field, getattr(config, field)) for field, _ in config._fields_)

    def get_config_defaults(self):
        """Get the default configuration from the device"""
        config = DeviceConfigStruct()
        dll.ifx_device_get_config_defaults(self.handle, byref(config))
        check_rc()
        # return struct as dictionary
        return dict((field, getattr(config, field)) for field, _ in config._fields_)

    def get_metrics_defaults(self):
        """Get the default metrics from the device"""
        metrics = DeviceMetricsStruct()
        dll.ifx_device_get_metrics_defaults(self.handle, byref(metrics))
        check_rc()
        # return struct as dictionary
        return dict((field, getattr(metrics, field)) for field, _ in metrics._fields_)    

    def start_acquisition(self):
        """Start acquisition of time domain data

        Starts the acquisition of time domain data from the connected device.
        If the data acquisition is already running the function has no effect.
        """
        ret = dll.ifx_device_start_acquisition(self.handle)
        check_rc()
        return ret

    def stop_acquisition(self):
        """Stop acquisition of time domain data

        Stops the acquisition of time domain data from the connected device.
        If the data acquisition is already stopped the function has no effect.
        """
        ret = dll.ifx_device_stop_acquisition(self.handle)
        check_rc()
        return ret

    def get_next_frame(self, frame, timeout_ms=None):
        """Retrieve next frame of time domain data from device

        Retrieve the next complete frame of time domain data from the connected
        device. The samples from all chirps and all enabled RX antennas will be
        copied to the provided data structure frame.

        If timeout_ms is given, an IFX_ERROR_TIMEOUT exception is thrown if a
        complete frame is not given within timeout_ms miliseconds.
        """
        if timeout_ms:
            ret = dll.ifx_device_get_next_frame_timeout(self.handle, frame.handle, timeout_ms)
        else:
            ret = dll.ifx_device_get_next_frame(self.handle, frame.handle)
        check_rc(ret)

    def create_frame_from_device_handle(self):
        """Create frame for time domain data acquisition

        This method checks the current configuration of the specified sensor
        device and initializes a data structure that can hold a time domain
        data frame according acquired through that device.
        """
        frame_p = dll.ifx_device_create_frame_from_device_handle(self.handle)
        check_rc()
        return Frame.create_from_pointer(frame_p)

    def get_shield_uuid(self):
        """Get the unique id for the radar shield"""
        c_uuid = dll.ifx_device_get_shield_uuid(self.handle)
        check_rc()
        return c_uuid.decode("utf-8")

    def get_temperature(self):
        """Get the temperature of the device in degrees Celsius

        Note that reading the temperature is not supported for UTR11. An
        exception will be raised in this case.
        """
        temperature = c_float(0)
        dll.ifx_device_get_temperature(self.handle, pointer(temperature))
        check_rc()
        return float(temperature.value)

    def get_firmware_information(self):
        info_p = dll.ifx_device_get_firmware_information(self.handle)
        check_rc()
        return dict((field, getattr(info_p.contents, field)) for field, _ in info_p.contents._fields_)

    def get_device_information(self):
        info_p = dll.ifx_device_get_device_information(self.handle)
        check_rc()
        d = dict((field, getattr(info_p.contents, field)) for field, _ in info_p.contents._fields_)
        d["shield_type"] = ShieldType(d["shield_type"])
        return d

    def get_register_list_string(self,trigger):
        """Get the exported register list as a hexadecimal string"""
        ptr = dll.ifx_device_register_list_string(self.handle,trigger)
        check_rc()
        reg_list_string = cast(ptr, c_char_p).value
        reg_list_string_py = reg_list_string.decode('ascii')
        dll.ifx_mem_free(ptr)
        return reg_list_string_py

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.__del__()

    def __del__(self):
        """Destroy device handle"""
        if hasattr(self, "handle") and self.handle:
            dll.ifx_device_destroy(self.handle)
            self.handle = None
