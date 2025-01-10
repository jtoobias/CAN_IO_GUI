#!/usr/bin/env python3
import canopen
import os
import time
import numpy as np

class CANBusHandler:

    # SDO's
    __TSDO = 0x580		# Transmitted by the CAN IO board
    __RSDO = 0x600		# Received by the CAN IO board
    # heartbeat
    __HEARTBEAT = 0x700

    # SDO write commands (respond with success)
    __WR_CLIENT_REQUEST_CMD_1_BYTE = 0x2F
    __WR_CLIENT_REQUEST_CMD_2_BYTE = 0x2B
    __WR_CLIENT_REQUEST_CMD_3_BYTE = 0x27
    __WR_CLIENT_REQUEST_CMD_4_BYTE = 0x23

    # SDO read commands
    __RD_CLIENT_REQUEST_CMD_BYTE    = 0x40
    __RD_SERVER_RESPONSE_CMD_1_BYTE = 0x4F
    __RD_SERVER_RESPONSE_CMD_2_BYTE = 0x4B
    __RD_SERVER_RESPONSE_CMD_3_BYTE = 0x47
    __RD_SERVER_RESPONSE_CMD_4_BYTE = 0x43

    __CAN_SERVER_RESPONSE_SUCCESS   = 0x60
    __CAN_SERVER_RESPONSE_ERROR     = 0x80

    __ERROR_REG_INDEX_OD            = 0x1001
    __DERROR_REG_SUBINDEX_OD        = 0x00
    __HEARTBEAT_INDEX_OD            = 0x1017
    __HEARTBEAT_SUBINDEX_OD         = 0x00
    __ID_OBJECT_OD                  = 0x1018
    __ID_OBJECT_NUM_ENTRIES_OD      = 0x00
    __ID_OBJECT_VENDOR_ID_OD        = 0x01
    __ID_OBJECT_PRODUCT_CODE_OD     = 0x02
    __ID_OBJECT_REVISION_NUM_OD     = 0x03


    __INPUT_INDEX_OD                = 0x6000
    __INPUT_SUBINDEX_OD             = 0x00
    __OUTPUT_INDEX_OD               = 0x6200
    __OUTPUT_SUBINDEX_OD            = 0x00

    __TEMP_INDEX_OD                 = 0x6002
    __TEMP_SUBINDEX_OD              = 0x00
    __ACCEL_INDEX_OD                = 0x6003
    __ACCEL_X_SUBINDEX_OD           = 0x00
    __ACCEL_Y_SUBINDEX_OD           = 0x01
    __ACCEL_Z_SUBINDEX_OD           = 0x02
    __GYRO_INDEX_OD                 = 0x6004
    __GYRO_X_SUBINDEX_OD            = 0x00
    __GYRO_Y_SUBINDEX_OD            = 0x01
    __GYRO_Z_SUBINDEX_OD            = 0x02

    def __init__(self):
        # Start with creating a network representing one CAN bus
        self.network = canopen.Network()
        self.node = None
        self.node_id = 3
        self.baud_rate = 500*1000


    def connect_device(self,device_name:str,buad_rate:int) -> bool:
        print (self.node_id)
        if (self.node_id == None or self.node_id == 0): return False
        device_path = '/dev/serial/by-id/'+device_name
        print ("conneting: ",device_path)
        self.network.connect(bustype='seeedstudio', 
                        channel=device_path,
                        bitrate=buad_rate)
        
        file_name = "CAN_IO.eds"
        file_path = os.path.join("~/software/CAN_IO/resources", file_name)
        # Expand ~ to the full home directory path
        expanded_path = os.path.expanduser(file_path)
        self.node = canopen.RemoteNode(3, expanded_path)
        self.network.add_node(self.node)
        return True

    
    def start_can_node(self):
        if (self.node == None): 
            print ("Node not connected")
            return
        print ("Start")
        self.node.nmt.state = 'OPERATIONAL'

    def stop_can_node(self):
        if (self.node == None): 
            print ("Node not connected")
            return
        print ("Stop")
        self.node.nmt.state = 'STOPPED'

    def reset_comms_can_node(self):
        if (self.node == None): 
            print ("Node not connected")
            return
        print ("Reset Comms")
        self.node.nmt.state = 'RESET COMMUNICATION'

    def restart_can_node(self):
        if (self.node == None): 
            print ("Node not connected")
            return
        print ("Restart")
        self.node.nmt.state = 'RESET'
        
    def disconnect_device(self,device_name:str,buad_rate:int):
        self.network.disconnect()

    def sdo_set_outputs(self,output_value:int):
        if (self.node == None): 
            print ("Node not connected")
            return
        self.node.sdo[0x6200].raw = output_value
        # self._send_message(self.__RSDO,[output_value])

    def sdo_read_inputs(self) -> int:
        if (self.node == None): 
            return
        return self.node.sdo[0x6000].raw
    
    def sdo_read_temperature(self) -> float:
        if (self.node == None): 
            return None
        return self.node.sdo[0x6002].raw/10
    
    def sdo_read_accelerometer_data(self) -> list[float]:
        if (self.node == None): 
            return None
        x_accel = self.node.sdo[0x6003][0x00].raw/100
        y_accel = self.node.sdo[0x6003][0x01].raw/100
        z_accel = self.node.sdo[0x6003][0x02].raw/100
        return [x_accel,y_accel,z_accel]
    
    def sdo_read_gyro_data(self) -> list[float]:
        if (self.node == None): 
            return None
        x_gyro = self.node.sdo[0x6004][0x00].raw/100
        y_gyro = self.node.sdo[0x6004][0x01].raw/100
        z_gyro = self.node.sdo[0x6004][0x02].raw/100
        return [x_gyro,y_gyro,z_gyro]

    def read_message(self):
        """Read a CAN message."""
        message = self.bus.recv(timeout=1)  # Timeout in seconds
        if message:
            return message.arbitration_id, message.data
        return None, None
    

    def _send_message(self,func_code,data:list[int]) -> bool:
        cob_id = func_code | self.node_id
        print (f"{cob_id:X}")
        if (len(data) == 1): cmd = self.__WR_CLIENT_REQUEST_CMD_1_BYTE.to_bytes(1, byteorder='little')
        elif (len(data) == 2): cmd = self.__WR_CLIENT_REQUEST_CMD_2_BYTE.to_bytes(1, byteorder='little')
        elif (len(data) == 3): cmd = self.__WR_CLIENT_REQUEST_CMD_3_BYTE.to_bytes(1, byteorder='little')
        elif (len(data) == 4): cmd = self.__WR_CLIENT_REQUEST_CMD_4_BYTE.to_bytes(1, byteorder='little')
        else: return False
        print (cmd)
        index = self.__OUTPUT_INDEX_OD.to_bytes(2, byteorder='little')
        print (index)
        sub_index = self.__OUTPUT_SUBINDEX_OD.to_bytes(1, byteorder='little')
        print (sub_index)
        tmp_val = 0
        offset = len(data)
        for d in data:
            offset -= 1
            tmp_val += (d << (8*offset))
        data_b = tmp_val.to_bytes(len(data), byteorder='little')
        print (data_b)
        payload = cmd + index + sub_index + data_b
        print (payload)
        self.network.send_message(cob_id,payload,False)
        return True
