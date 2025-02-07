#!/usr/bin/env python3
import canopen
import os
import time
import numpy as np
import struct
from Frontend.src.pdo_config import PDOconfig, TPDOconfig

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

    # RPDO Communication Parameters
    __RPDO1_COMM_PARAM_OD = 0x1400
    __RPDO2_COMM_PARAM_OD = 0x1401
    __RPDO3_COMM_PARAM_OD = 0x1402
    __RPDO4_COMM_PARAM_OD = 0x1403

# TPDO Communication Parameters
    __TPDO1_COMM_PARAM_OD = 0x1800
    __TPDO2_COMM_PARAM_OD = 0x1801
    __TPDO3_COMM_PARAM_OD = 0x1802
    __TPDO4_COMM_PARAM_OD = 0x1803

    __PDO_COMM_PARAM_COB_ID_SUBINDEX_OD         = 0x01
    __PDO_COMM_PARAM_TRANS_TYPE_SUBINDEX_OD     = 0x02
    __PDO_COMM_PARAM_INHIBIT_TIME_SUBINDEX_OD   = 0x03
    __PDO_COMM_PARAM_RESERVED_SUBINDEX_OD 		= 0x04
    __PDO_COMM_PARAM_EVENT_TIMER_SUBINDEX_OD	= 0x05

# RPDO Mapping Parameters
    __RPDO1_MAPPING_PARAM_OD = 0x1600
    __RPDO2_MAPPING_PARAM_OD = 0x1601
    __RPDO3_MAPPING_PARAM_OD = 0x1602
    __RPDO4_MAPPING_PARAM_OD = 0x1603

# TPDO Mapping Parameters
    __TPDO1_MAPPING_PARAM_OD = 0x1A00
    __TPDO2_MAPPING_PARAM_OD = 0x1A01
    __TPDO3_MAPPING_PARAM_OD = 0x1A02
    __TPDO4_MAPPING_PARAM_OD = 0x1A03

    __PDO_MAPPING_SUBINDEX_NUM_ENTRIES_OD = 0x00 # Subindex for number of entries
    __PDO_MAPPING_SUBINDEX_ENTRY_1_OD = 0x01 # Subindex for first entry
    __PDO_MAPPING_SUBINDEX_ENTRY_2_OD = 0x02 # Subindex for second entry
    __PDO_MAPPING_SUBINDEX_ENTRY_3_OD = 0x03 # Subindex for third entry
    __PDO_MAPPING_SUBINDEX_ENTRY_4_OD = 0x04 # Subindex for fourth entry
    __PDO_MAPPING_SUBINDEX_ENTRY_5_OD = 0x05 # Subindex for fifth entry
    __PDO_MAPPING_SUBINDEX_ENTRY_6_OD = 0x06 # Subindex for sixth entry
    __PDO_MAPPING_SUBINDEX_ENTRY_7_OD = 0x07 # Subindex for seventh entry
    __PDO_MAPPING_SUBINDEX_ENTRY_8_OD = 0x08 # Subindex for eighth entry

# TPDO1 Analog Thresholds and Trigger Directions
    __TPDO1_ANALOG_THRESHOLDS_OD    = 0x2000
    __TPDO1_TRIGGER_DIRS_OD         = 0x2001

# TPDO2 Analog Thresholds and Trigger Directions
    __TPDO2_ANALOG_THRESHOLDS_OD    = 0x2010
    __TPDO2_TRIGGER_DIRS_OD         = 0x2011

# TPDO3 Analog Thresholds and Trigger Directions
    __TPDO3_ANALOG_THRESHOLDS_OD    = 0x2020
    __TPDO3_TRIGGER_DIRS_OD         = 0x2021

# TPDO4 Analog Thresholds and Trigger Directions
    __TPDO4_ANALOG_THRESHOLDS_OD    = 0x2030
    __TPDO4_TRIGGER_DIRS_OD         = 0x2031


    #  Trigger sub_indices
    __TRIGGER_IN_1_SUBINDEX_OD = 0x01
    __TRIGGER_IN_2_SUBINDEX_OD = 0x02
    __TRIGGER_IN_3_SUBINDEX_OD = 0x03
    __TRIGGER_IN_4_SUBINDEX_OD = 0x04
    __TRIGGER_IN_5_SUBINDEX_OD = 0x05
    __TRIGGER_IN_6_SUBINDEX_OD = 0x06
    __TRIGGER_IN_7_SUBINDEX_OD = 0x07
    __TRIGGER_IN_8_SUBINDEX_OD = 0x08
    __TRIGGER_GYRO_X_SUBINDEX_OD = 0x09
    __TRIGGER_GYRO_Y_SUBINDEX_OD = 0x0A
    __TRIGGER_GYRO_Z_SUBINDEX_OD = 0x0B
    __TRIGGER_ACCEL_X_SUBINDEX_OD = 0x0C
    __TRIGGER_ACCEL_Y_SUBINDEX_OD = 0x0D
    __TRIGGER_ACCEL_Z_SUBINDEX_OD = 0x0E

    __ANALOG_NUMBER_SUBINDEX_OD   = 0x00
    __ANALOG_INPUT_1_SUBINDEX_OD  = 0x01
    __ANALOG_INPUT_2_SUBINDEX_OD  = 0x02
    __ANALOG_INPUT_3_SUBINDEX_OD  = 0x03
    __ANALOG_INPUT_4_SUBINDEX_OD  = 0x04
    __ANALOG_INPUT_5_SUBINDEX_OD  = 0x05
    __ANALOG_INPUT_6_SUBINDEX_OD  = 0x06


    __INPUT_INDEX_OD                = 0x6000
    __INPUT_SUBINDEX_OD             = 0x00
    OUTPUT_INDEX_OD               = 0x6200
    OUTPUT_SUBINDEX_OD            = 0x00

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

    
    def start_can_node(self,sync_enabled,sync_period):
        if (self.node == None): 
            print ("Node not connected")
            return
        print ("Start")
        self.node.nmt.state = 'OPERATIONAL'
        if (sync_enabled):self.network.sync.start(sync_period)


    def stop_can_node(self):
        if (self.node == None): 
            print ("Node not connected")
            return
        print ("Stop")
        self.node.nmt.state = 'STOPPED'
        self.network.sync.stop()

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
        tmp_val = self.to_int16(self.little_endian_to_big_endian(self.node.sdo[0x6002].raw,2))/10
        time.sleep(0.01)
        # print (f"{tmp_val:X} {tmp_val}")
        return tmp_val
    
    def sdo_read_accelerometer_data(self) -> list[float]:
        if (self.node == None): 
            return None
        tmp_val = self.node.sdo[0x6003][0x01].raw
        print (f"{tmp_val:X} {self.little_endian_to_big_endian(tmp_val,2):X}")
        x_accel = self.to_int16(self.little_endian_to_big_endian(tmp_val,2))/100
        time.sleep(0.01)
        y_accel = self.to_int16(self.little_endian_to_big_endian(self.node.sdo[0x6003][0x02].raw,2))/100
        time.sleep(0.01)
        z_accel = self.to_int16(self.little_endian_to_big_endian(self.node.sdo[0x6003][0x03].raw,2))/100
        time.sleep(0.01)
        return [x_accel,y_accel,z_accel]
    
    def sdo_read_gyro_data(self) -> list[float]:
        if (self.node == None): 
            return None
        x_gyro = self.to_int16(self.little_endian_to_big_endian(self.node.sdo[0x6004][0x01].raw,2))/100
        time.sleep(0.01)
        y_gyro = self.to_int16(self.little_endian_to_big_endian(self.node.sdo[0x6004][0x02].raw,2))/100
        time.sleep(0.01)
        z_gyro = self.to_int16(self.little_endian_to_big_endian(self.node.sdo[0x6004][0x03].raw,2))/100
        time.sleep(0.01)
        return [x_gyro,y_gyro,z_gyro]
    
    def pdo_read_accelerometer_data(self) -> list[float]:
        if (self.node == None): 
            return None
        tmp_val = self.node.tpdo
        print (f"{tmp_val:X} {self.little_endian_to_big_endian(tmp_val,2):X}")
        x_accel = self.to_int16(self.little_endian_to_big_endian(tmp_val,2))/100
        time.sleep(0.01)
        y_accel = self.to_int16(self.little_endian_to_big_endian(self.node.sdo[0x6003][0x02].raw,2))/100
        time.sleep(0.01)
        z_accel = self.to_int16(self.little_endian_to_big_endian(self.node.sdo[0x6003][0x03].raw,2))/100
        time.sleep(0.01)
        return [x_accel,y_accel,z_accel]
    
    def update_pdo_comms_parameters(self,pdo:PDOconfig|TPDOconfig):
        index = 0
        if (pdo.pdo_type == "T"):
            if (pdo.pdo_num == 1): index = self.__TPDO1_COMM_PARAM_OD
            elif (pdo.pdo_num == 2): index = self.__TPDO2_COMM_PARAM_OD
            elif (pdo.pdo_num == 3): index = self.__TPDO3_COMM_PARAM_OD
            elif (pdo.pdo_num == 4): index = self.__TPDO4_COMM_PARAM_OD
            else: 
                print ("RPDO number not correct: ",pdo.pdo_num) 
                return
        elif (pdo.pdo_type == "R"):
            if (pdo.pdo_num == 1): index = self.__RPDO1_COMM_PARAM_OD
            elif (pdo.pdo_num == 2): index = self.__RPDO2_COMM_PARAM_OD
            elif (pdo.pdo_num == 3): index = self.__RPDO3_COMM_PARAM_OD
            elif (pdo.pdo_num == 4): index = self.__RPDO4_COMM_PARAM_OD
            else: 
                print ("RPDO number not correct: ",pdo.pdo_num) 
                return
        else:
            print ("PDO type not correct: ",pdo.pdo_type) 

        if (pdo.cob_id > -1): 
            print (f"Sending COB id: {pdo.cob_id:X}")
            self.send_sdo(index,self.__PDO_COMM_PARAM_COB_ID_SUBINDEX_OD,pdo.cob_id)
            time.sleep(0.05)
        if (pdo.transmission_type_value > -1): 
            self.send_sdo(index,self.__PDO_COMM_PARAM_TRANS_TYPE_SUBINDEX_OD,pdo.transmission_type_value)
            time.sleep(0.05)
        if (pdo.inhibit_time > -1): 
            self.send_sdo(index,self.__PDO_COMM_PARAM_INHIBIT_TIME_SUBINDEX_OD,pdo.inhibit_time)
            time.sleep(0.05)
        if (pdo.transmit_period > -1): 
            self.send_sdo(index,self.__PDO_COMM_PARAM_EVENT_TIMER_SUBINDEX_OD,pdo.transmit_period)
            time.sleep(0.05)

    def update_pdo_mapped_indices(self,pdo:PDOconfig|TPDOconfig):
        if (pdo.pdo_type == "T"):
            if (pdo.pdo_num == 1): index = self.__TPDO1_MAPPING_PARAM_OD
            elif (pdo.pdo_num == 2): index = self.__TPDO2_MAPPING_PARAM_OD
            elif (pdo.pdo_num == 3): index = self.__TPDO3_MAPPING_PARAM_OD
            elif (pdo.pdo_num == 4): index = self.__TPDO4_MAPPING_PARAM_OD
            else: 
                print ("RPDO number not correct: ",pdo.pdo_num) 
                return
        elif (pdo.pdo_type == "R"):
            if (pdo.pdo_num == 1): index = self.__RPDO1_MAPPING_PARAM_OD
            elif (pdo.pdo_num == 2): index = self.__RPDO2_MAPPING_PARAM_OD
            elif (pdo.pdo_num == 3): index = self.__RPDO3_MAPPING_PARAM_OD
            elif (pdo.pdo_num == 4): index = self.__RPDO4_MAPPING_PARAM_OD
            else: 
                print ("RPDO number not correct: ",pdo.pdo_num) 
                return
        else:
            print ("PDO type not correct: ",pdo.pdo_type) 

        for offset,mapped_index in enumerate(pdo.mapped_indices):
            if (mapped_index == -1): break
            print (mapped_index)
            self.send_sdo(index,(self.__PDO_MAPPING_SUBINDEX_ENTRY_1_OD+offset),mapped_index)
            time.sleep(0.05)

    def update_tpdo_triggers(self,tpdo:TPDOconfig):
        if (tpdo.pdo_num == 1): index = self.__TPDO1_TRIGGER_DIRS_OD
        elif (tpdo.pdo_num == 2): index = self.__TPDO2_TRIGGER_DIRS_OD
        elif (tpdo.pdo_num == 3): index = self.__TPDO3_TRIGGER_DIRS_OD
        elif (tpdo.pdo_num == 4): index = self.__TPDO4_TRIGGER_DIRS_OD
        
        for offset,tValue in enumerate(tpdo.triggers):
            print (f"Value: {tValue} Index: {index:X} subIndex: {(self.__TRIGGER_IN_1_SUBINDEX_OD+offset):X}")
            # self.send_sdo(index,(self.__TRIGGER_IN_1_SUBINDEX_OD+offset),tValue)

            self._send_message(self.__RSDO,1,index,(self.__TRIGGER_IN_1_SUBINDEX_OD+offset),1,[tValue])
            time.sleep(0.05)

    def update_tpdo_analog_thresholds(self,tpdo:TPDOconfig):
        if (tpdo.pdo_num == 1): index = self.__TPDO1_ANALOG_THRESHOLDS_OD
        elif (tpdo.pdo_num == 2): index = self.__TPDO2_ANALOG_THRESHOLDS_OD
        elif (tpdo.pdo_num == 3): index = self.__TPDO3_ANALOG_THRESHOLDS_OD
        elif (tpdo.pdo_num == 4): index = self.__TPDO4_ANALOG_THRESHOLDS_OD
        
        for offset,aValue in enumerate(tpdo.analog_thresholds):
            if (aValue == None): continue
            self.send_sdo(index,(self.__ANALOG_INPUT_1_SUBINDEX_OD+offset),aValue)
            time.sleep(0.05)
    
    def update_tpdo_config(self,tpdo:TPDOconfig):
        self.update_pdo_comms_parameters(tpdo)
        print ("Comms params completed")
        self.update_pdo_mapped_indices(tpdo)
        print ("Mapped params completed")
        self.update_tpdo_analog_thresholds(tpdo)
        print ("Analog Thresholds completed")
        self.update_tpdo_triggers(tpdo)
        print ("Triggers completed")

    def update_rpdo_config(self,rpdo:PDOconfig):
        self.update_pdo_comms_parameters(rpdo)
        self.update_pdo_mapped_indices(rpdo)
        
    def send_sdo(self,index,sub_index,data:int):
        if (sub_index == 0): 
            self.node.sdo[index].raw = data
        else: 
            print (f"Data being Sent: {data} {index:X} {sub_index}",data)
            self.node.sdo[index][sub_index].raw = data

    def to_int16(self,value):
        # Ensure the value is within the 16-bit signed integer range
        if value < -32768 or value > 32767:
            # Use modulo and mask to wrap the value within the int16 range
            value = (value + 32768) % 65536 - 32768  # Wrap using modulo
        
        return value

    def read_message(self):
        """Read a CAN message."""
        message = self.network.bus.recv(timeout=1)  # Timeout in seconds
        if message:
            return message.arbitration_id, message.data
        return None, None
    
    def little_endian_to_big_endian(self,value,byte_len) -> int:

        # Swap the byte order
        if (byte_len == 1): big_endian_value = value
        elif (byte_len == 2): big_endian_value = ((value & 0x00FF) << 8) | ((value & 0xFF00) >> 8)
        elif (byte_len == 3): big_endian_value = ((value & 0x0000FF) << 16) | ((value & 0xFF0000) >> 16)
        elif (byte_len == 4): big_endian_value = (((value & 0x000000FF) << 24) | ((value & 0xFF000000) >> 24) | (value & 0x0000FF00) << 8) | ((value & 0x00FF0000) >> 8)
        else: big_endian_value = -100000000
        return big_endian_value
    

    def _send_message(self,func_code:int,operation:int,index:int,sub_index:int,num_bytes:int,data:list[int]) -> bool:
        cob_id = func_code | self.node_id
        # print (f"{cob_id:X}")
        if (operation == 1):
            if (num_bytes == 1): cmd = self.__WR_CLIENT_REQUEST_CMD_1_BYTE.to_bytes(1, byteorder='little')
            elif (num_bytes == 2): cmd = self.__WR_CLIENT_REQUEST_CMD_2_BYTE.to_bytes(1, byteorder='little')
            elif (num_bytes == 3): cmd = self.__WR_CLIENT_REQUEST_CMD_3_BYTE.to_bytes(1, byteorder='little')
            elif (num_bytes == 4): cmd = self.__WR_CLIENT_REQUEST_CMD_4_BYTE.to_bytes(1, byteorder='little')
            else: return False
        else:
            cmd = self.__RD_CLIENT_REQUEST_CMD_BYTE.to_bytes(1, byteorder='little')
        # print (cmd)
        bit_index = index.to_bytes(2, byteorder='little')
        # print (bit_index)
        bit_sub_index = sub_index.to_bytes(1, byteorder='little')
        # print (bit_sub_index)
        tmp_val = 0
        offset = len(data)
        # print (data)
        for d in data:
            offset -= 1
            tmp_val += (d << (8*offset))
        data_b = tmp_val.to_bytes(len(data), byteorder='little')
        # print (data_b)
        payload = cmd + bit_index + bit_sub_index + data_b
        # print (payload)
        self.network.send_message(cob_id,payload,False)
        return True
