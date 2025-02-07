from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt,QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow,QWidget,QCheckBox
from Frontend.src.CAN_IO_GUI import Ui_MainWindow
from Backend.can_handler import CANBusHandler
from Frontend.src.pdo_config import PDOconfig, TPDOconfig, get_value_from_text_box
import sys
import os
from functools import partial
import struct

G_ACCEL = 9.80665

class RunningAvg():
  def __init__(self,buffer_size):
    self.running_avg_size = buffer_size
    self.buffer = [0.0]*self.running_avg_size
    self.index = 0
    self.count = 0
    self.value = 0.0

  def update_running_avg(self,new_value):
      """Add a new value and return the running average."""
      # Replace the oldest value with the new one
      self.buffer[self.index] = new_value
      # Move index forward cyclically
      self.index = (self.index + 1) % self.running_avg_size
      # Increase count until the buffer is full
      if self.count < self.running_avg_size:
        self.count += 1
      # Compute and return the average
      self.value = sum(self.buffer[:self.count]) / self.count
  
class CustomComboBox(QtWidgets.QComboBox):
  def showPopup(self):
    """Override showPopup to update the items before showing."""
    self.populate_connections_cb()
    super().showPopup()  # Call the parent method to show the popup

  def populate_connections_cb(self):
    """Populate the ComboBox with serial devices."""
    self.clear()
    serial_by_id_path = "/dev/serial/by-id/"

    try:
      devices = os.listdir(serial_by_id_path)
      if devices:
        print("Serial devices in /dev/serial/by-id/:")
        for d in devices:
          print(d)
        self.addItems(devices)
      else:
        print("No devices found in /dev/serial/by-id/.")
    except FileNotFoundError:
      print(f"The directory {serial_by_id_path} does not exist.")
    except Exception as e:
      print(f"An error occurred: {e}")

class MainWindow(QMainWindow):

    def __init__(self):
      super().__init__()
      self.ui = Ui_MainWindow()
      self.ui.setupUi(self)
      self.can_handler = CANBusHandler()
      
      self.sync_period = 0
      self.sync_enabled = False
        # Use the custom ComboBox
      self.ui.comboBoxConnections = CustomComboBox(self.ui.comboBoxConnections)
      self.ui.comboBoxBaudRates.addItems(["1000","500","250","125","62.5"])
      self.check_boxes_states = 0

      self.tpdo1 = TPDOconfig(self.ui.TPDO_tab_widget,1,"T")
      self.tpdo2 = TPDOconfig(self.ui.TPDO_tab_widget,2,"T")
      self.tpdo3 = TPDOconfig(self.ui.TPDO_tab_widget,3,"T")
      self.tpdo4 = TPDOconfig(self.ui.TPDO_tab_widget,4,"T")
      
      self.rpdo1 = PDOconfig(self.ui.RPDO_tab_widget,1,"R")
      self.rpdo2 = PDOconfig(self.ui.RPDO_tab_widget,2,"R")
      self.rpdo3 = PDOconfig(self.ui.RPDO_tab_widget,3,"R")
      self.rpdo4 = PDOconfig(self.ui.RPDO_tab_widget,4,"R")
      # Connect signals (e.g., buttons or checkboxes)
      self.setup_connections()
      self.connect_existing_checkboxes()


      self.known_output_state = 0
      self.known_input_state = 0

      self.accel_x_avg = RunningAvg(3)
      self.accel_y_avg = RunningAvg(3)
      self.accel_z_avg = RunningAvg(3)
      self.gyro_x_avg = RunningAvg(3)
      self.gyro_y_avg = RunningAvg(3)
      self.gyro_z_avg = RunningAvg(3)



      # self.can_handler.node.tpdo[1].enabled = True   
        # Set up the timer to call update_label every 100ms
      self.timer = QTimer(self)
      # self.timer.timeout.connect(self.update_periodic_data)

      # This needs to be handles better. Check the indices for the tpdo and handle accordingly
    def tpdo_cb(self,message,tpdo:PDOconfig):
      # data_set = False
      data_offset = 0
        # loop through mapped indices and load the correct data and transmit
      for k,mapped_index in enumerate(tpdo.mapped_indices):
        if (mapped_index == -1): break
        index = mapped_index >> 16
        sub_index = (mapped_index >> 8) & 0xFF
        number_bytes = int((mapped_index & 0xFF)/8)
        # print (f"{mapped_index:X}, {data_offset}, {number_bytes}, {index}, {sub_index}")
        # Retrieve the correct amount of bytes
        tmp_val = struct.unpack('<h', message.data[data_offset:(data_offset+number_bytes)])[0]
        # Increment the data offset for correct data collection next time
        data_offset += number_bytes

        if (index == self.can_handler.INPUT_INDEX_OD):
          current_input_states = self.can_handler.to_int16(tmp_val)
          self.update_input_indicators(current_input_states)
          self.known_input_state = current_input_states
        elif (index == self.can_handler.OUTPUT_INDEX_OD):
          current_output_states = self.can_handler.to_int16(tmp_val)
          self.update_output_indicators(current_output_states)
          self.known_output_state = current_output_states
        elif (index == self.can_handler.TEMP_INDEX_OD):
          tmp_val /= 10
          self.ui.TempLcd.display(tmp_val)
        elif (index == self.can_handler.ACCEL_INDEX_OD):
          tmp_val /= 100
          if (sub_index == self.can_handler.ACCEL_X_SUBINDEX_OD):
            self.accel_x_avg.update_running_avg(tmp_val)
            self.ui.AccelLcdX.display(tmp_val)
          elif (sub_index == self.can_handler.ACCEL_Y_SUBINDEX_OD):
            self.accel_y_avg.update_running_avg(tmp_val)
            self.ui.AccelLcdY.display(tmp_val)
          elif (sub_index == self.can_handler.ACCEL_Z_SUBINDEX_OD):
            self.accel_z_avg.update_running_avg(tmp_val)
            self.ui.AccelLcdZ.display(tmp_val)
        elif (index == self.can_handler.GYRO_INDEX_OD):
          tmp_val /= 100
          if (sub_index == self.can_handler.GYRO_X_SUBINDEX_OD):
            self.gyro_x_avg.update_running_avg(tmp_val)
            self.ui.GyroLcdX.display(tmp_val)
          elif (sub_index == self.can_handler.GYRO_Y_SUBINDEX_OD):
            self.gyro_x_avg.update_running_avg(tmp_val)
            self.ui.GyroLcdY.display(tmp_val)
          elif (sub_index == self.can_handler.GYRO_Z_SUBINDEX_OD):
            self.gyro_x_avg.update_running_avg(tmp_val)
            self.ui.GyroLcdZ.display(tmp_val)
        else:
          print (f"Mapped index doesn't align with what is usable for TPDO: {mapped_index} {k}")
          
    def tpdo1_cb(self,message):
      # Handle Acceleration data
      # print(f"Received TPDO {message.cob_id:#04X}: {message.data.hex()}")
      # Extract values
      if not message.data:  
        print("Error: TPDO1 message.data is empty!")
        return
      self.tpdo_cb(message,self.tpdo1)

    def tpdo2_cb(self,message):
      if not message.data:  
        print("Error: TPDO2 message.data is empty!")
        return
      
      self.tpdo_cb(message,self.tpdo2)
    
    def tpdo3_cb(self,message):
      # Handle IO data
      if not message.data:  
        print("Error: TPDO3 message.data is empty!")
        return
      self.tpdo_cb(message,self.tpdo3)

    def update_input_indicators(self,input_status:int):
      self.change_io_indicator_background(self.ui.DI_LED_widget_1,input_status,self.known_input_state,0x01)
      self.change_io_indicator_background(self.ui.DI_LED_widget_2,input_status,self.known_input_state,0x02)
      self.change_io_indicator_background(self.ui.DI_LED_widget_3,input_status,self.known_input_state,0x04)
      self.change_io_indicator_background(self.ui.DI_LED_widget_4,input_status,self.known_input_state,0x08)
      self.change_io_indicator_background(self.ui.DI_LED_widget_5,input_status,self.known_input_state,0x10)
      self.change_io_indicator_background(self.ui.DI_LED_widget_6,input_status,self.known_input_state,0x20)
      self.change_io_indicator_background(self.ui.DI_LED_widget_7,input_status,self.known_input_state,0x40)
      self.change_io_indicator_background(self.ui.DI_LED_widget_8,input_status,self.known_input_state,0x80)
    
    
    def update_output_indicators(self,output_status:int):
      self.change_io_indicator_background(self.ui.D0_LED_widget_1,output_status,self.known_output_state,0x01)
      self.change_io_indicator_background(self.ui.D0_LED_widget_2,output_status,self.known_output_state,0x02)
      self.change_io_indicator_background(self.ui.D0_LED_widget_3,output_status,self.known_output_state,0x04)
      self.change_io_indicator_background(self.ui.D0_LED_widget_4,output_status,self.known_output_state,0x08)
      self.change_io_indicator_background(self.ui.D0_LED_widget_5,output_status,self.known_output_state,0x10)
      self.change_io_indicator_background(self.ui.D0_LED_widget_6,output_status,self.known_output_state,0x20)
      self.change_io_indicator_background(self.ui.D0_LED_widget_7,output_status,self.known_output_state,0x40)
      self.change_io_indicator_background(self.ui.D0_LED_widget_8,output_status,self.known_output_state,0x80)

    def change_io_indicator_background(self,widget:QWidget,io_state:int,known_io_state:int,bit_mask:int):
        # Is there a Change on that bit? 
      if ((io_state & bit_mask) != (known_io_state & bit_mask)):
        if (io_state & bit_mask): widget.setStyleSheet("background-color: rgb(46, 204, 113);")  # Green
        else:widget.setStyleSheet("background-color: rgb(192, 192, 192);")  # Green


    def update_periodic_data(self):
      #  pass
       accel_data = self.can_handler.sdo_read_accelerometer_data()
       if (accel_data == None): return
       self.ui.AccelLcdX.display(accel_data[0])
       self.ui.AccelLcdY.display(accel_data[1])
       self.ui.AccelLcdZ.display(accel_data[2])

       gyro_data = self.can_handler.sdo_read_gyro_data()
       if (gyro_data == None): return
       self.ui.GyroLcdX.display(gyro_data[0])
       self.ui.GyroLcdY.display(gyro_data[1])
       self.ui.GyroLcdZ.display(gyro_data[2])

       temperature = self.can_handler.sdo_read_temperature()
       if (temperature == None): return
       self.ui.TempLcd.display(temperature)

    def connect_existing_checkboxes(self):
        # Iterate through the existing layout items
        for i in range(self.ui.OutputLayout.count()):
            widget = self.ui.OutputLayout.itemAt(i).widget()
            if isinstance(widget, QCheckBox):  # Check if the widget is a checkbox
                widget.stateChanged.connect(self.on_checkbox_changed)

    def on_checkbox_changed(self, state):
        # Find which checkbox triggered the signal
        checkbox = self.sender()
        if isinstance(checkbox, QCheckBox):
          position = int(checkbox.text())-1
          print ("Pos: ",position)
          if (state == 2):
            self.check_boxes_states |= 1 << position
          else:
            self.check_boxes_states &= (0xFF ^(1 << position))
          
          print(f"{checkbox.text()} changed to {state} {'Checked' if state == 2 else 'Unchecked'}")
      
    def on_temperature_offset_button_clicked(self):
      temperature_offset = get_value_from_text_box(self.ui.lineEdit_TempOffset.text())
      # Send sdo 
      self.can_handler.sdo_set_temperature_offset(temperature_offset)

    def on_imu_offset_button_clicked(self):
      # z value should be 'g' x and y = 0 for accelerometer
      # gyro values should be zeros
      # Use the average value to set offsets
      accel_offsets = []
      gyro_offsets = []
      accel_offsets.append(-self.accel_x_avg.value)
      accel_offsets.append(-self.accel_y_avg.value)
      accel_offsets.append(-(self.accel_z_avg.value-G_ACCEL))
      gyro_offsets.append(-self.gyro_x_avg.value)
      gyro_offsets.append(-self.gyro_y_avg.value)
      gyro_offsets.append(-self.gyro_z_avg.value)
      # Send sdo 
      self.can_handler.sdo_set_imu_offsets(accel_offsets,gyro_offsets)

    def setup_connections(self):
      # Example: Connect a button to a method
      self.ui.ButtonConnect.clicked.connect(self.handle_connect_button_click)
      self.ui.ButtonOutput.clicked.connect(self.handle_set_outputs_button_click)
      self.ui.ButtonNMTStart.clicked.connect(partial(self.can_handler.start_can_node, self.sync_enabled, self.sync_period))
      self.ui.ButtonNMTStop.clicked.connect(self.can_handler.stop_can_node)
      self.ui.ButtonNMTRestart.clicked.connect(self.can_handler.restart_can_node)
      self.ui.ButtonNMTResetComms.clicked.connect(self.can_handler.reset_comms_can_node)

      self.ui.PDO_apply_button.clicked.connect(self.handle_pdo_apply_button_click)
      # Example: Connect a checkbox to a method
      self.ui.checkBoxOut1.stateChanged.connect(self.handle_checkbox_state_change)

      self.ui.lineEdit_sync_period.returnPressed.connect(self.sync_on_enter_pressed)
      self.ui.checkBox_sync_enable.stateChanged.connect(self.sync_checkbox_toggled)

      self.ui.ButtonRPDO1Send.clicked.connect(partial(self.handle_rpdo_button_click, self.rpdo1,1))
      self.ui.ButtonRPDO2Send.clicked.connect(partial(self.handle_rpdo_button_click, self.rpdo2,2))
      self.ui.ButtonRPDO3Send.clicked.connect(partial(self.handle_rpdo_button_click, self.rpdo3,3))
      self.ui.ButtonRPDO4Send.clicked.connect(partial(self.handle_rpdo_button_click, self.rpdo4,4))

      self.ui.ButtonIMUOffset.clicked.connect(self.on_imu_offset_button_clicked)
      self.ui.ButtonIMU_TempOffset.clicked.connect(self.on_temperature_offset_button_clicked)

    def sync_on_enter_pressed(self):
      self.sync_period = get_value_from_text_box(self.ui.lineEdit_sync_period.text())
    
    def sync_checkbox_toggled(self):
      try:
        if self.ui.checkBox_sync_enable.isChecked():
          if (self.sync_period == None): 
            print ("Sync period is incorrect: \"None\"")
            return
          self.can_handler.network.sync.start((self.sync_period/1000))
          self.sync_enabled = True
        else:
          self.can_handler.network.sync.stop()
          self.sync_enabled = False
      except:
        print ("Make sure the network is setup")

    def handle_pdo_apply_button_click(self):
      self.tpdo1.update_tpdo_config()
      self.tpdo2.update_tpdo_config()
      self.tpdo3.update_tpdo_config()
      self.tpdo4.update_tpdo_config()

      self.rpdo1.update_general_pdo_config()
      self.rpdo2.update_general_pdo_config()
      self.rpdo3.update_general_pdo_config()
      self.rpdo4.update_general_pdo_config()

      # self.can_handler.update_pdo_mapped_indices(self.tpdo1)

      # self.can_handler.update_tpdo_config(self.tpdo1)

      self.can_handler.update_tpdo_config(self.tpdo1)
      print ("TPDO1 Complete")
      self.can_handler.update_tpdo_config(self.tpdo2)
      print ("TPDO2 Complete")
      self.can_handler.update_tpdo_config(self.tpdo3)
      print ("TPDO3 Complete")
      self.can_handler.update_tpdo_config(self.tpdo4)
      print ("TPDO4 Complete")
      
      self.can_handler.update_rpdo_config(self.rpdo1)
      print ("RPDO1 Complete")
      self.can_handler.update_rpdo_config(self.rpdo2)
      print ("RPDO2 Complete")
      self.can_handler.update_rpdo_config(self.rpdo3)
      print ("RPDO3 Complete")
      self.can_handler.update_rpdo_config(self.rpdo4)
      print ("RPDO4 Complete")
      
    def handle_rpdo_button_click(self,rpdo:PDOconfig,rpdo_num:int):
      data_set = False
      num_bits = []
      data = []
        # loop through mapped indices and load the correct data and transmit
      for k,mapped_index in enumerate(rpdo.mapped_indices):
        if (mapped_index == -1): break
        index = mapped_index >> 16
        num_bytes = mapped_index & 0xFF
        sub_index = (mapped_index >> 8) & 0xFF
        if (index == self.can_handler.OUTPUT_INDEX_OD):
          num_bits.append(num_bytes)
          data.append(self.check_boxes_states)
          data_set = True
        else:
          print (f"Mapped index doesn't align with what is usable for RPDO: {mapped_index} {k}")
      if (data_set): 
        self.can_handler.send_rpdo_message(rpdo.cob_id,num_bits,data)

    def handle_connect_button_click(self):
      print("Button clicked!")
      device = self.ui.comboBoxConnections.currentText()
      # need to handle only numbers
      self.can_handler.node_id = int(self.ui.spinBox_CAN_ID.value())
      
      self.can_handler.baud_rate = float(self.ui.comboBoxBaudRates.currentText())*1000
      print("Connect to ",device)
      print(self.can_handler.connect_device(device,self.can_handler.baud_rate))

      # Configure the PDO's
      self.can_handler.node.tpdo[1].add_callback(self.tpdo1_cb)
      self.can_handler.node.tpdo[1].cob_id = 0x183  # Set custom COB-ID
      self.can_handler.node.tpdo[1].enabled = True   # Ensure TPDO is enabled

      self.can_handler.node.tpdo[2].add_callback(self.tpdo2_cb)
      self.can_handler.node.tpdo[2].cob_id = 0x283  # Set custom COB-ID
      self.can_handler.node.tpdo[2].enabled = True   # Ensure TPDO is enabled
      
      self.can_handler.node.tpdo[3].add_callback(self.tpdo3_cb)
      self.can_handler.node.tpdo[3].cob_id = 0x383  # Set custom COB-ID
      self.can_handler.node.tpdo[3].enabled = True   # Ensure TPDO is enabled
      self.can_handler.node.tpdo.subscribe()

      # self.can_handler.node.tpdo.save()              # Save settings
      # print(f"Mapped objects: {self.can_handler.node.tpdo[1].map}")

      # Update the status bar
      self.ui.statusbar.showMessage("Button was clicked!", 3000)
      
    def handle_set_outputs_button_click(self):
      print(f"Output Button clicked! {self.check_boxes_states:X}")
        # Send output update to the device
      self.can_handler.sdo_set_outputs(self.check_boxes_states)

    def handle_checkbox_state_change(self, state):
      if state == 2:  # Checked state
          print("Checkbox checked!")
      else:
          print("Checkbox unchecked!")

    
if __name__ == "__main__":
  app = QApplication(sys.argv)
  main_window = MainWindow()
  main_window.show()
  sys.exit(app.exec())
