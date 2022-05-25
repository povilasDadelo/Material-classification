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

import numpy as np
import matplotlib.pyplot as plt
from ifxRadarSDK import *


print ("Radar SDK Version: " + get_version_full())

# open device: The device will be closed at the end of the block. Instead of
# the with-block you can also use:
#   device = Device()
# However, the with block gives you better control when the device is closed.
with Device() as device:
    # activate all RX antennas
    num_rx_antennas = device.get_device_information()["num_rx_antennas"]
    rx_mask = (1 << num_rx_antennas) - 1

    # trying out my configs
    metric = {
            'sample_rate_Hz':           1000000,
            'range_resolution_m':       0.03,
            'max_range_m':              0.8,
            'max_speed_m_s':            2.84,
            'speed_resolution_m_s':     0.089,
            'center_frequency_Hz':      0,
            # 'lower_frequency_Hz':       57810000000,
            # 'upper_frequency_Hz':       63190000000,
            'rx_mask':                  rx_mask,
            'tx_mask':                  1,
            'tx_power_level':           4,
            'if_gain_dB':               40}

    cfg = device.translate_metrics_to_config(**metric);
    print("Config", "\n", cfg)

    # set device config
    # device.set_config()
    device.set_config(**cfg)
    
    # print(device.get_device_information())
    

    # create frame
    frame = device.create_frame_from_device_handle()

    # number of virtual active receiving antennas
    num_rx = frame.get_num_rx()
    print("Number of antennas in use ", num_rx)

    # A loop for fetching a finite number of frames comes next..
    for frame_number in range(1):
        try:
            device.get_next_frame(frame)
        except ErrorFifoOverflow:
            print("Fifo Overflow")
            exit(1)

        # Do some processing with the obtained frame.
        # In this example we just dump it into the console
        print ("Got frame " + format(frame_number) + ", num_antennas={}".format(num_rx))

        for iAnt in range(0, num_rx):
            mat = frame.get_mat_from_antenna(iAnt)
            print("Antenna", iAnt, "\n", mat.shape)
            plt.imshow(mat)
            # plt.colorbar()
            plt.show()
