#!/usr/bin/env python3
import canopen
import os
import time
import struct
from Frontend.pdo_config import PDOconfig


class CANBusHandler:
    __INT32_MAX = (1 << 31) - 1
    __ANALOG_INVALID_NUMBER = __INT32_MAX
    # SDO's
    __TSDO = 0x580  # Transmitted by the CAN IO board
    __RSDO = 0x600  # Received by the CAN IO board
    # heartbeat
    __HEARTBEAT = 0x700

    # SDO write commands (respond with success)
    __WR_CLIENT_REQUEST_CMD_1_BYTE = 0x2F
    __WR_CLIENT_REQUEST_CMD_2_BYTE = 0x2B
    __WR_CLIENT_REQUEST_CMD_3_BYTE = 0x27
    __WR_CLIENT_REQUEST_CMD_4_BYTE = 0x23

    # SDO read commands
    __RD_CLIENT_REQUEST_CMD_BYTE = 0x40
    __RD_SERVER_RESPONSE_CMD_1_BYTE = 0x4F
    __RD_SERVER_RESPONSE_CMD_2_BYTE = 0x4B
    __RD_SERVER_RESPONSE_CMD_3_BYTE = 0x47
    __RD_SERVER_RESPONSE_CMD_4_BYTE = 0x43

    __CAN_SERVER_RESPONSE_SUCCESS = 0x60
    __CAN_SERVER_RESPONSE_ERROR = 0x80

    __ERROR_REG_INDEX_OD = 0x1001
    __DERROR_REG_SUBINDEX_OD = 0x00
    __HEARTBEAT_INDEX_OD = 0x1017
    __HEARTBEAT_SUBINDEX_OD = 0x00
    __ID_OBJECT_OD = 0x1018
    __ID_OBJECT_NUM_ENTRIES_OD = 0x00
    __ID_OBJECT_VENDOR_ID_OD = 0x01
    __ID_OBJECT_PRODUCT_CODE_OD = 0x02
    __ID_OBJECT_REVISION_NUM_OD = 0x03

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

    __PDO_COMM_PARAM_COB_ID_SUBINDEX_OD = 0x01
    __PDO_COMM_PARAM_TRANS_TYPE_SUBINDEX_OD = 0x02
    __PDO_COMM_PARAM_INHIBIT_TIME_SUBINDEX_OD = 0x03
    __PDO_COMM_PARAM_RESERVED_SUBINDEX_OD = 0x04
    __PDO_COMM_PARAM_EVENT_TIMER_SUBINDEX_OD = 0x05

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

    __PDO_MAPPING_SUBINDEX_NUM_ENTRIES_OD = 0x00  # Subindex for number of entries
    __PDO_MAPPING_SUBINDEX_ENTRY_1_OD = 0x01  # Subindex for first entry
    __PDO_MAPPING_SUBINDEX_ENTRY_2_OD = 0x02  # Subindex for second entry
    __PDO_MAPPING_SUBINDEX_ENTRY_3_OD = 0x03  # Subindex for third entry
    __PDO_MAPPING_SUBINDEX_ENTRY_4_OD = 0x04  # Subindex for fourth entry
    __PDO_MAPPING_SUBINDEX_ENTRY_5_OD = 0x05  # Subindex for fifth entry
    __PDO_MAPPING_SUBINDEX_ENTRY_6_OD = 0x06  # Subindex for sixth entry
    __PDO_MAPPING_SUBINDEX_ENTRY_7_OD = 0x07  # Subindex for seventh entry
    __PDO_MAPPING_SUBINDEX_ENTRY_8_OD = 0x08  # Subindex for eighth entry

    __TPDO1_ANALOG_THRESHOLDS_OD = 0x2000
    __TPDO1_TRIGGER_DIRS_OD = 0x2001
    __RPDO1_ANALOG_THRESHOLDS_OD = 0x2002
    __RPDO1_TRIGGER_DIRS_OD = 0x2003

    # TPDO2 Analog Thresholds and Trigger Directions
    __TPDO2_ANALOG_THRESHOLDS_OD = 0x2010
    __TPDO2_TRIGGER_DIRS_OD = 0x2011
    __RPDO3_ANALOG_THRESHOLDS_OD = 0x2022
    __RPDO3_TRIGGER_DIRS_OD = 0x2023

    # TPDO3 Analog Thresholds and Trigger Directions
    __TPDO3_ANALOG_THRESHOLDS_OD = 0x2020
    __TPDO3_TRIGGER_DIRS_OD = 0x2021
    __RPDO2_ANALOG_THRESHOLDS_OD = 0x2012
    __RPDO2_TRIGGER_DIRS_OD = 0x2013

    # TPDO4 Analog Thresholds and Trigger Directions
    __TPDO4_ANALOG_THRESHOLDS_OD = 0x2030
    __TPDO4_TRIGGER_DIRS_OD = 0x2031
    __RPDO4_ANALOG_THRESHOLDS_OD = 0x2032
    __RPDO4_TRIGGER_DIRS_OD = 0x2033

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

    __ANALOG_NUMBER_SUBINDEX_OD = 0x00
    __ANALOG_INPUT_1_SUBINDEX_OD = 0x01
    __ANALOG_INPUT_2_SUBINDEX_OD = 0x02
    __ANALOG_INPUT_3_SUBINDEX_OD = 0x03
    __ANALOG_INPUT_4_SUBINDEX_OD = 0x04
    __ANALOG_INPUT_5_SUBINDEX_OD = 0x05
    __ANALOG_INPUT_6_SUBINDEX_OD = 0x06

    INPUT_INDEX_OD = 0x6000
    INPUT_SUBINDEX_OD = 0x00
    OUTPUT_INDEX_OD = 0x6200
    OUTPUT_SUBINDEX_OD = 0x00

    TEMP_INDEX_OD = 0x6002
    TEMP_SUBINDEX_OD = 0x00
    ACCEL_INDEX_OD = 0x6003
    ACCEL_X_SUBINDEX_OD = 0x01
    ACCEL_Y_SUBINDEX_OD = 0x02
    ACCEL_Z_SUBINDEX_OD = 0x03
    GYRO_INDEX_OD = 0x6004
    GYRO_X_SUBINDEX_OD = 0x01
    GYRO_Y_SUBINDEX_OD = 0x02
    GYRO_Z_SUBINDEX_OD = 0x03
    DEVICE_STATE_OD = 0x7000

    CAN_STATE_OFF = 0
    CAN_STATE_INIT = 1
    CAN_STATE_PREOPERATIONAL = 2
    CAN_STATE_OPERATIONAL = 3
    CAN_STATE_STOPPED = 4

    def __init__(self):
        # Start with creating a network representing one CAN bus
        self.network = canopen.Network()
        self.node = None
        self.node_id = 3
        self.baud_rate = 500 * 1000

    def connect_device(self, device_name: str, buad_rate: int) -> bool:
        print(self.node_id)
        if self.node_id is None or self.node_id == 0:
            return False
        device_path = "/dev/serial/by-id/" + device_name
        print("conneting: ", device_path)
        self.network.connect(bustype="seeedstudio", channel=device_path, bitrate=buad_rate)

        file_name = "CAN_IO.eds"
        file_path = os.path.join("~/software/CAN_IO/resources", file_name)
        # Expand ~ to the full home directory path
        expanded_path = os.path.expanduser(file_path)
        self.node = canopen.RemoteNode(3, expanded_path)
        self.network.add_node(self.node)
        # print(self.node.sdo.od.indices)
        return True

    def start_can_node(self, sync_enabled, sync_period):
        if self.node is None:
            print("Node not connected")
            return
        print("Start")
        self.node.nmt.state = "OPERATIONAL"
        if sync_enabled:
            self.network.sync.start(sync_period)

    def stop_can_node(self):
        if self.node is None:
            print("Node not connected")
            return
        print("Stop")
        self.node.nmt.state = "STOPPED"
        self.network.sync.stop()

    def reset_comms_can_node(self):
        if self.node is None:
            print("Node not connected")
            return
        print("Reset Comms")
        self.node.nmt.state = "RESET COMMUNICATION"

    def restart_can_node(self):
        if self.node is None:
            print("Node not connected")
            return
        print("Restart")
        self.node.nmt.state = "RESET"

    def disconnect_device(self, device_name: str, buad_rate: int):
        self.network.disconnect()

    def sdo_set_outputs(self, output_value: int):
        if self.node is None:
            print("Node not connected")
            return
        self.node.sdo[0x6200].raw = output_value
        # self._send_message(self.__RSDO,[output_value])

    def sdo_set_temperature_offset(self, temperature_offset: int):
        if self.node is None:
            print("Node not connected")
            return
        self.node.sdo[0x3002].raw = temperature_offset * 10

    def sdo_set_imu_offsets(self, accel_offset, gyro_offset: int):
        if self.node is None:
            print("Node not connected")
            return
        for i in range(len(accel_offset)):
            self.node.sdo[0x3000][i + 1].raw = accel_offset[i] * 100
            time.sleep(0.05)
            self.node.sdo[0x3001][i + 1].raw = gyro_offset[i] * 100
            time.sleep(0.05)

    def sdo_read_inputs(self) -> int:
        if self.node is None:
            return
        return self.node.sdo[0x6000].raw

    def sdo_read_device_state(self) -> int:
        if self.node is None:
            return
        return self.node.sdo[0x7000].raw

    def sdo_save_device_config(self, save_val: int) -> int:
        if self.node is None:
            return
        self.node.sdo[0x1010].raw = save_val

    def sdo_read_temperature(self) -> float:
        if self.node is None:
            return None
        tmp_val = self.to_int16(self.little_endian_to_big_endian(self.node.sdo[0x6002].raw, 2)) / 10
        time.sleep(0.01)
        # print (f"{tmp_val:X} {tmp_val}")
        return tmp_val

    def sdo_read_accelerometer_data(self) -> list[float]:
        if self.node is None:
            return None
        tmp_val = self.node.sdo[0x6003][0x01].raw
        print(f"{tmp_val:X} {self.little_endian_to_big_endian(tmp_val, 2):X}")
        x_accel = self.to_int16(self.little_endian_to_big_endian(tmp_val, 2)) / 100
        time.sleep(0.01)
        y_accel = (
            self.to_int16(self.little_endian_to_big_endian(self.node.sdo[0x6003][0x02].raw, 2))
            / 100
        )
        time.sleep(0.01)
        z_accel = (
            self.to_int16(self.little_endian_to_big_endian(self.node.sdo[0x6003][0x03].raw, 2))
            / 100
        )
        time.sleep(0.01)
        return [x_accel, y_accel, z_accel]

    def sdo_read_gyro_data(self) -> list[float]:
        if self.node is None:
            return None
        x_gyro = (
            self.to_int16(self.little_endian_to_big_endian(self.node.sdo[0x6004][0x01].raw, 2))
            / 100
        )
        time.sleep(0.01)
        y_gyro = (
            self.to_int16(self.little_endian_to_big_endian(self.node.sdo[0x6004][0x02].raw, 2))
            / 100
        )
        time.sleep(0.01)
        z_gyro = (
            self.to_int16(self.little_endian_to_big_endian(self.node.sdo[0x6004][0x03].raw, 2))
            / 100
        )
        time.sleep(0.01)
        return [x_gyro, y_gyro, z_gyro]

    def tpdo_read_accelerometer_data(self) -> list[float]:
        if self.node is None:
            return None
        tmp_val = self.node.tpdo
        print(f"{tmp_val:X} {self.little_endian_to_big_endian(tmp_val, 2):X}")
        x_accel = self.to_int16(self.little_endian_to_big_endian(tmp_val, 2)) / 100
        time.sleep(0.01)
        y_accel = (
            self.to_int16(self.little_endian_to_big_endian(self.node.sdo[0x6003][0x02].raw, 2))
            / 100
        )
        time.sleep(0.01)
        z_accel = (
            self.to_int16(self.little_endian_to_big_endian(self.node.sdo[0x6003][0x03].raw, 2))
            / 100
        )
        time.sleep(0.01)
        return [x_accel, y_accel, z_accel]

    def upload_pdo_config(self, pdo: PDOconfig):
        index = 0
        if pdo.pdo_type == "T":
            if pdo.pdo_num == 1:
                index = self.__TPDO1_COMM_PARAM_OD
            elif pdo.pdo_num == 2:
                index = self.__TPDO2_COMM_PARAM_OD
            elif pdo.pdo_num == 3:
                index = self.__TPDO3_COMM_PARAM_OD
            elif pdo.pdo_num == 4:
                index = self.__TPDO4_COMM_PARAM_OD
            else:
                print("TPDO number not correct: ", pdo.pdo_num)
                return
        elif pdo.pdo_type == "R":
            if pdo.pdo_num == 1:
                index = self.__RPDO1_COMM_PARAM_OD
            elif pdo.pdo_num == 2:
                index = self.__RPDO2_COMM_PARAM_OD
            elif pdo.pdo_num == 3:
                index = self.__RPDO3_COMM_PARAM_OD
            elif pdo.pdo_num == 4:
                index = self.__RPDO4_COMM_PARAM_OD
            else:
                print("RPDO number not correct: ", pdo.pdo_num)
                return
        else:
            print("PDO type not correct: ", pdo.pdo_type)

        pdo.cob_id = self.little_endian_to_big_endian(
            self.node.sdo[index][self.__PDO_COMM_PARAM_COB_ID_SUBINDEX_OD].raw, 4
        )

        time.sleep(0.04)
        pdo.transmission_type_value = self.node.sdo[index][
            self.__PDO_COMM_PARAM_TRANS_TYPE_SUBINDEX_OD
        ].raw
        time.sleep(0.04)
        pdo.inhibit_time = self.little_endian_to_big_endian(
            self.node.sdo[index][self.__PDO_COMM_PARAM_INHIBIT_TIME_SUBINDEX_OD].raw, 4
        )
        time.sleep(0.04)
        pdo.transmit_period = self.little_endian_to_big_endian(
            self.node.sdo[index][self.__PDO_COMM_PARAM_EVENT_TIMER_SUBINDEX_OD].raw, 4
        )
        time.sleep(0.04)

        if pdo.pdo_type == "T":
            if pdo.pdo_num == 1:
                index = self.__TPDO1_MAPPING_PARAM_OD
            elif pdo.pdo_num == 2:
                index = self.__TPDO2_MAPPING_PARAM_OD
            elif pdo.pdo_num == 3:
                index = self.__TPDO3_MAPPING_PARAM_OD
            elif pdo.pdo_num == 4:
                index = self.__TPDO4_MAPPING_PARAM_OD
            else:
                print("TPDO number not correct: ", pdo.pdo_num)
                return
        elif pdo.pdo_type == "R":
            if pdo.pdo_num == 1:
                index = self.__RPDO1_MAPPING_PARAM_OD
            elif pdo.pdo_num == 2:
                index = self.__RPDO2_MAPPING_PARAM_OD
            elif pdo.pdo_num == 3:
                index = self.__RPDO3_MAPPING_PARAM_OD
            elif pdo.pdo_num == 4:
                index = self.__RPDO4_MAPPING_PARAM_OD
            else:
                print("RPDO number not correct: ", pdo.pdo_num)
                return
        else:
            print("PDO type not correct: ", pdo.pdo_type)
        for offset in range(len(pdo.mapped_indices)):
            print(
                f"{pdo.pdo_type} - {pdo.pdo_num} - {index:X} {(self.__PDO_MAPPING_SUBINDEX_ENTRY_1_OD+offset):X}"
            )
            mapped_index = self.little_endian_to_big_endian(
                self.node.sdo[index][(self.__PDO_MAPPING_SUBINDEX_ENTRY_1_OD + offset)].raw,
                4,
            )

            if mapped_index > 0:
                pdo.mapped_indices[offset] = mapped_index
            else:
                pdo.mapped_indices[offset] = -1
            time.sleep(0.04)

    def upload_pdo_triggers(self, pdo: PDOconfig):
        if pdo.pdo_type == "T":
            if pdo.pdo_num == 1:
                index = self.__TPDO1_TRIGGER_DIRS_OD
            elif pdo.pdo_num == 2:
                index = self.__TPDO2_TRIGGER_DIRS_OD
            elif pdo.pdo_num == 3:
                index = self.__TPDO3_TRIGGER_DIRS_OD
            elif pdo.pdo_num == 4:
                index = self.__TPDO4_TRIGGER_DIRS_OD
            else:
                print("TPDO number not correct: ", pdo.pdo_num)
                return
        elif pdo.pdo_type == "R":
            if pdo.pdo_num == 1:
                index = self.__RPDO1_TRIGGER_DIRS_OD
            elif pdo.pdo_num == 2:
                index = self.__RPDO2_TRIGGER_DIRS_OD
            elif pdo.pdo_num == 3:
                index = self.__RPDO3_TRIGGER_DIRS_OD
            elif pdo.pdo_num == 4:
                index = self.__RPDO4_TRIGGER_DIRS_OD
            else:
                print("RPDO number not correct: ", pdo.pdo_num)
                return
        else:
            print("PDO type not correct: ", pdo.pdo_type)

        for offset in range(len(pdo.triggers)):
            print(
                f"{pdo.pdo_type} - {pdo.pdo_num} - {index:X} {(self.__TRIGGER_IN_1_SUBINDEX_OD+offset):X}"
            )
            pdo.triggers[offset] = self.node.sdo[index][
                (self.__TRIGGER_IN_1_SUBINDEX_OD + offset)
            ].raw
            time.sleep(0.04)

        if pdo.pdo_type == "T":
            if pdo.pdo_num == 1:
                index = self.__TPDO1_ANALOG_THRESHOLDS_OD
            elif pdo.pdo_num == 2:
                index = self.__TPDO2_ANALOG_THRESHOLDS_OD
            elif pdo.pdo_num == 3:
                index = self.__TPDO3_ANALOG_THRESHOLDS_OD
            elif pdo.pdo_num == 4:
                index = self.__TPDO4_ANALOG_THRESHOLDS_OD
            else:
                print("TPDO number not correct: ", pdo.pdo_num)
                return
        elif pdo.pdo_type == "R":
            if pdo.pdo_num == 1:
                index = self.__RPDO1_ANALOG_THRESHOLDS_OD
            elif pdo.pdo_num == 2:
                index = self.__RPDO2_ANALOG_THRESHOLDS_OD
            elif pdo.pdo_num == 3:
                index = self.__RPDO3_ANALOG_THRESHOLDS_OD
            elif pdo.pdo_num == 4:
                index = self.__RPDO4_ANALOG_THRESHOLDS_OD
            else:
                print("RPDO number not correct: ", pdo.pdo_num)
                return
        else:
            print("PDO type not correct: ", pdo.pdo_type)

        for offset in range(len(pdo.analog_thresholds)):
            print(
                f"{pdo.pdo_type} - {pdo.pdo_num} - {index:X} {(self.__ANALOG_INPUT_1_SUBINDEX_OD+offset):X}"
            )
            pdo.analog_thresholds[offset] = self.little_endian_to_big_endian(
                self.node.sdo[index][(self.__ANALOG_INPUT_1_SUBINDEX_OD + offset)].raw,
                2,
            )
            if pdo.analog_thresholds[offset] == self.__ANALOG_INVALID_NUMBER:
                pdo.analog_thresholds[offset] = None
            time.sleep(0.04)

    def update_pdo_comms_parameters(self, pdo: PDOconfig):
        index = 0
        if pdo.pdo_type == "T":
            if pdo.pdo_num == 1:
                index = self.__TPDO1_COMM_PARAM_OD
            elif pdo.pdo_num == 2:
                index = self.__TPDO2_COMM_PARAM_OD
            elif pdo.pdo_num == 3:
                index = self.__TPDO3_COMM_PARAM_OD
            elif pdo.pdo_num == 4:
                index = self.__TPDO4_COMM_PARAM_OD
            else:
                print("TPDO number not correct: ", pdo.pdo_num)
                return
        elif pdo.pdo_type == "R":
            if pdo.pdo_num == 1:
                index = self.__RPDO1_COMM_PARAM_OD
            elif pdo.pdo_num == 2:
                index = self.__RPDO2_COMM_PARAM_OD
            elif pdo.pdo_num == 3:
                index = self.__RPDO3_COMM_PARAM_OD
            elif pdo.pdo_num == 4:
                index = self.__RPDO4_COMM_PARAM_OD
            else:
                print("RPDO number not correct: ", pdo.pdo_num)
                return
        else:
            print("PDO type not correct: ", pdo.pdo_type)

        if pdo.cob_id > -1:
            self.send_sdo(index, self.__PDO_COMM_PARAM_COB_ID_SUBINDEX_OD, pdo.cob_id)
            time.sleep(0.04)
        if pdo.transmission_type_value > -1:
            self.send_sdo(
                index,
                self.__PDO_COMM_PARAM_TRANS_TYPE_SUBINDEX_OD,
                pdo.transmission_type_value,
            )
            time.sleep(0.04)
        if pdo.inhibit_time > -1:
            self.send_sdo(index, self.__PDO_COMM_PARAM_INHIBIT_TIME_SUBINDEX_OD, pdo.inhibit_time)
            time.sleep(0.04)
        if pdo.transmit_period > -1:
            self.send_sdo(
                index,
                self.__PDO_COMM_PARAM_EVENT_TIMER_SUBINDEX_OD,
                pdo.transmit_period,
            )
            time.sleep(0.04)

    def update_pdo_mapped_indices(self, pdo: PDOconfig):
        if pdo.pdo_type == "T":
            if pdo.pdo_num == 1:
                index = self.__TPDO1_MAPPING_PARAM_OD
            elif pdo.pdo_num == 2:
                index = self.__TPDO2_MAPPING_PARAM_OD
            elif pdo.pdo_num == 3:
                index = self.__TPDO3_MAPPING_PARAM_OD
            elif pdo.pdo_num == 4:
                index = self.__TPDO4_MAPPING_PARAM_OD
            else:
                print("RPDO number not correct: ", pdo.pdo_num)
                return
        elif pdo.pdo_type == "R":
            if pdo.pdo_num == 1:
                index = self.__RPDO1_MAPPING_PARAM_OD
            elif pdo.pdo_num == 2:
                index = self.__RPDO2_MAPPING_PARAM_OD
            elif pdo.pdo_num == 3:
                index = self.__RPDO3_MAPPING_PARAM_OD
            elif pdo.pdo_num == 4:
                index = self.__RPDO4_MAPPING_PARAM_OD
            else:
                print("RPDO number not correct: ", pdo.pdo_num)
                return
        else:
            print("PDO type not correct: ", pdo.pdo_type)

        for offset, mapped_index in enumerate(pdo.mapped_indices):
            if mapped_index == -1:
                break
            self.send_sdo(index, (self.__PDO_MAPPING_SUBINDEX_ENTRY_1_OD + offset), mapped_index)
            time.sleep(0.04)

    def update_pdo_triggers(self, pdo: PDOconfig):

        if pdo.pdo_type == "T":
            if pdo.pdo_num == 1:
                index = self.__TPDO1_TRIGGER_DIRS_OD
            elif pdo.pdo_num == 2:
                index = self.__TPDO2_TRIGGER_DIRS_OD
            elif pdo.pdo_num == 3:
                index = self.__TPDO3_TRIGGER_DIRS_OD
            elif pdo.pdo_num == 4:
                index = self.__TPDO4_TRIGGER_DIRS_OD
            else:
                print("RPDO number not correct: ", pdo.pdo_num)
                return
        elif pdo.pdo_type == "R":
            if pdo.pdo_num == 1:
                index = self.__RPDO1_TRIGGER_DIRS_OD
            elif pdo.pdo_num == 2:
                index = self.__RPDO2_TRIGGER_DIRS_OD
            elif pdo.pdo_num == 3:
                index = self.__RPDO3_TRIGGER_DIRS_OD
            elif pdo.pdo_num == 4:
                index = self.__RPDO4_TRIGGER_DIRS_OD
            else:
                print("RPDO number not correct: ", pdo.pdo_num)
                return
        else:
            print("PDO type not correct: ", pdo.pdo_type)

        for offset, tValue in enumerate(pdo.triggers):
            self.send_sdo(index, (self.__TRIGGER_IN_1_SUBINDEX_OD + offset), tValue)
            time.sleep(0.04)

    def update_pdo_analog_thresholds(self, pdo: PDOconfig):

        if pdo.pdo_type == "T":
            if pdo.pdo_num == 1:
                index = self.__TPDO1_ANALOG_THRESHOLDS_OD
            elif pdo.pdo_num == 2:
                index = self.__TPDO2_ANALOG_THRESHOLDS_OD
            elif pdo.pdo_num == 3:
                index = self.__TPDO3_ANALOG_THRESHOLDS_OD
            elif pdo.pdo_num == 4:
                index = self.__TPDO4_ANALOG_THRESHOLDS_OD
            else:
                print("RPDO number not correct: ", pdo.pdo_num)
                return
        elif pdo.pdo_type == "R":
            if pdo.pdo_num == 1:
                index = self.__RPDO1_ANALOG_THRESHOLDS_OD
            elif pdo.pdo_num == 2:
                index = self.__RPDO2_ANALOG_THRESHOLDS_OD
            elif pdo.pdo_num == 3:
                index = self.__RPDO3_ANALOG_THRESHOLDS_OD
            elif pdo.pdo_num == 4:
                index = self.__RPDO4_ANALOG_THRESHOLDS_OD
            else:
                print("RPDO number not correct: ", pdo.pdo_num)
                return
        else:
            print("PDO type not correct: ", pdo.pdo_type)

        print(f"ANALOG Sends: {pdo.pdo_type} - {pdo.pdo_num} - {index}")

        for offset, aValue in enumerate(pdo.analog_thresholds):
            if aValue is None:
                continue
            self.send_sdo(index, (self.__ANALOG_INPUT_1_SUBINDEX_OD + offset), aValue)
            time.sleep(0.04)

    def update_pdo_config(self, pdo: PDOconfig):
        self.update_pdo_comms_parameters(pdo)
        self.update_pdo_mapped_indices(pdo)
        self.update_pdo_analog_thresholds(pdo)
        self.update_pdo_triggers(pdo)

    def send_sdo(self, index, sub_index, data: int):
        try:
            if sub_index == 0:
                self.node.sdo[index].raw = data
            else:
                # print (f"Data being Sent: {data} {index:X} {sub_index}",data)
                self.node.sdo[index][sub_index].raw = data
        except Exception as e:
            print(
                f"Send was not completed: index: {index} sub-index: {sub_index}, data: {data}, {e}"
            )

    def to_int16(self, value):
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

    def little_endian_to_big_endian(self, value, byte_len) -> int:

        # Swap the byte order
        if byte_len == 1:
            big_endian_value = value
        elif byte_len == 2:
            big_endian_value = ((value & 0x00FF) << 8) | ((value & 0xFF00) >> 8)
        elif byte_len == 3:
            big_endian_value = ((value & 0x0000FF) << 16) | ((value & 0xFF0000) >> 16)
        elif byte_len == 4:
            big_endian_value = (
                ((value & 0x000000FF) << 24)
                | ((value & 0xFF000000) >> 24)
                | (value & 0x0000FF00) << 8
            ) | ((value & 0x00FF0000) >> 8)
        else:
            big_endian_value = -100000000
        return big_endian_value

    # def _send_message(self,func_code:int,operation:int,index:int,sub_index:int,num_bytes:int,data:list[int]) -> bool:
    #     cob_id = func_code | self.node_id
    #     # print (f"{cob_id:X}")
    #     if (operation == 1):
    #         if (num_bytes == 1): cmd = self.__WR_CLIENT_REQUEST_CMD_1_BYTE.to_bytes(1, byteorder='little')
    #         elif (num_bytes == 2): cmd = self.__WR_CLIENT_REQUEST_CMD_2_BYTE.to_bytes(1, byteorder='little')
    #         elif (num_bytes == 3): cmd = self.__WR_CLIENT_REQUEST_CMD_3_BYTE.to_bytes(1, byteorder='little')
    #         elif (num_bytes == 4): cmd = self.__WR_CLIENT_REQUEST_CMD_4_BYTE.to_bytes(1, byteorder='little')
    #         else: return False
    #     else:
    #         cmd = self.__RD_CLIENT_REQUEST_CMD_BYTE.to_bytes(1, byteorder='little')
    #     # print (cmd)
    #     bit_index = index.to_bytes(2, byteorder='little')
    #     # print (bit_index)
    #     bit_sub_index = sub_index.to_bytes(1, byteorder='little')
    #     # print (bit_sub_index)
    #     tmp_val = 0
    #     offset = len(data)
    #     # print (data)
    #     for d in data:
    #         offset -= 1
    #         tmp_val += (d << (8*offset))
    #     data_b = tmp_val.to_bytes(len(data), byteorder='little')
    #     # print (data_b)
    #     payload = cmd + bit_index + bit_sub_index + data_b
    #     # print (payload)
    #     self.network.send_message(cob_id,payload,False)
    #     return True

    def _send_message(
        self,
        func_code: int,
        operation: int,
        index: int,
        sub_index: int,
        num_bytes: int,
        data: list[int] = None,
    ) -> list[int] | bool:
        cob_id = func_code | self.node_id

        if operation == 1:  # Write operation
            if num_bytes == 1:
                cmd = self.__WR_CLIENT_REQUEST_CMD_1_BYTE.to_bytes(1, byteorder="little")
            elif num_bytes == 2:
                cmd = self.__WR_CLIENT_REQUEST_CMD_2_BYTE.to_bytes(1, byteorder="little")
            elif num_bytes == 3:
                cmd = self.__WR_CLIENT_REQUEST_CMD_3_BYTE.to_bytes(1, byteorder="little")
            elif num_bytes == 4:
                cmd = self.__WR_CLIENT_REQUEST_CMD_4_BYTE.to_bytes(1, byteorder="little")
            else:
                return False
        else:  # Read operation
            cmd = self.__RD_CLIENT_REQUEST_CMD_BYTE.to_bytes(1, byteorder="little")

        bit_index = index.to_bytes(2, byteorder="little")
        bit_sub_index = sub_index.to_bytes(1, byteorder="little")

        # Prepare data for write operation
        data_b = b""
        if operation == 1 and data is not None:
            tmp_val = sum((d << (8 * (len(data) - 1 - i))) for i, d in enumerate(data))
            data_b = tmp_val.to_bytes(len(data), byteorder="little")

        # Send request
        payload = cmd + bit_index + bit_sub_index + data_b
        self.network.send_message(cob_id, payload, False)

        if operation == 1:  # Write: No response expected
            return True

        # Wait for response (Read operation)
        timeout = 0.5  # Adjust timeout as needed
        start_time = time.time()

        while time.time() - start_time < timeout:
            message = self.network.receive_message()  # This should be a blocking or polling receive
            if message and message.cob_id == (0x580 | self.node_id):  # 0x580 = SDO response base
                if message.data[1:3] == bit_index and message.data[3] == sub_index:
                    return list(message.data[4:])  # Return received data (ignoring first 4 bytes)

        return False  # Timeout or no valid response received

    def send_rpdo_message(self, cob_id: int, num_bits: list[int], data: list[int]) -> bool:
        byte_format = []
        # print (f"Post: cid: {cob_id} ,Data: {data} bits: {num_bits}")
        # print (data)
        for d in num_bits:
            tmp_val = int(d / 8)
            if tmp_val == 1:
                byte_format.append("B")
            elif tmp_val == 2:
                byte_format.append("H")
            elif tmp_val == 3 and tmp_val == 4:
                byte_format.append("I")
            else:
                return False

        data_b = numbers_to_bytes(data, byte_format)

        self.network.send_message(cob_id, data_b, False)
        return True


def numbers_to_bytes(data_list, formats):
    """
    Convert a list of numbers into a byte array based on specified formats.

    :param data_list: List of numbers to be packed.
    :param formats: List of format specifiers (e.g., 'B' for 1 byte, 'H' for 2 bytes, 'I' for 4 bytes).
    :return: Byte array.
    """
    if len(data_list) != len(formats):
        raise ValueError("Each number must have a corresponding format specifier.")

    packed_bytes = b""

    for num, fmt in zip(data_list, formats):
        packed_bytes += struct.pack(fmt, num)

    return packed_bytes
