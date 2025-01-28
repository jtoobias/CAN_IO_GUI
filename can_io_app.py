from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt,QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow,QWidget,\
    QVBoxLayout, QCheckBox, QComboBox, QTableWidget, QSpinBox,QLineEdit
from Frontend.src.CAN_IO_GUI import Ui_MainWindow
from Backend.can_handler import CANBusHandler
import sys
import os


_ANALOG_THRESHOLD_GYRO_X = 0
_ANALOG_THRESHOLD_GYRO_Y = 1
_ANALOG_THRESHOLD_GYRO_Z = 2
_ANALOG_THRESHOLD_ACCEL_X = 3
_ANALOG_THRESHOLD_ACCEL_Y = 4
_ANALOG_THRESHOLD_ACCEL_Z = 5

_TRIGGER_MODE_DIN_1 = 0
_TRIGGER_MODE_DIN_2 = 1
_TRIGGER_MODE_DIN_3 = 2
_TRIGGER_MODE_DIN_4 = 3
_TRIGGER_MODE_DIN_5 = 4
_TRIGGER_MODE_DIN_6 = 5
_TRIGGER_MODE_DIN_7 = 6
_TRIGGER_MODE_DIN_8 = 7
_TRIGGER_MODE_GYRO_X = 8
_TRIGGER_MODE_GYRO_Y = 9
_TRIGGER_MODE_GYRO_Z = 10
_TRIGGER_MODE_ACCEL_X = 11
_TRIGGER_MODE_ACCEL_Y = 12
_TRIGGER_MODE_ACCEL_Z = 13


  
class PDOconfig():
  def __init__(self,tab:QWidget,pdo_num:int,pdo_type:str):
    self.tab = tab
    self.widgets = self.tab.findChildren(QWidget)
    self.pdo_num = pdo_num
    # "T" = TPDO, "R" = RPDO
    self.pdo_type = pdo_type  

    self.mapped_indices = [-1]*8
    self.cob_id = -1
    self.inhibit_time = -1
    self.transmit_period = -1
    self.transmission_type_value = -1

  def get_table_widget_item(self,table:QTableWidget,row:int,col:int):
    item = table.item(row, 0)  # Access the item in the first column
    if item and item.text():  # Check if item is not empty
      return int(item.text(), 16)
    else:
      return None

  def update_pdo_mapped_indices(self):
    try:
      tableWidget = self.tab.findChild(QTableWidget, f"tableWidget_{self.pdo_type}PDO{self.pdo_num}")
      row_count = tableWidget.rowCount()
      for row in range(row_count):
        if ((value := self.get_table_widget_item(tableWidget,row,0)) == None):
            # Make sure to clear the other potientially old entries
          self.mapped_indices[row:-1] = [0] * (len(self.mapped_indices) - row)
          break
        self.mapped_indices[row] = value

    except Exception as e:
      print (f"{self.pdo_type}PDO{self.pdo_num} APPLY Mapped Indices: ",e)

  def update_pdo_comms_parameters(self):
    try:
      value = self.tab.findChild(QLineEdit, f"COB_ID_box_{self.pdo_type}PDO{self.pdo_num}").text()
      if (value.isdigit()): self.cob_id = int(value)
      else: self.cob_id = -1
      value = int(self.tab.findChild(QLineEdit, f"Inhibit_time_box_{self.pdo_type}PDO{self.pdo_num}").text())
      if (value.isdigit()): self.inhibit_time = int(value)
      else: self.inhibit_time = -1
      value = int(self.tab.findChild(QLineEdit, f"Transmit_period_box_{self.pdo_type}PDO{self.pdo_num}").text())
      if (value.isdigit()): self.transmit_period = int(value)
      else: self.transmit_period = -1
      self.transmission_type_value = int(self.tab.findChild(QSpinBox, f"spinBox_{self.pdo_type}PDO{self.pdo_num}").value())
    except Exception as e:
      print (f"{self.pdo_type}PDO{self.pdo_num} APPLY Comms Params: ",e)

  def update_general_pdo_config(self):
    self.update_pdo_mapped_indices()
    self.update_pdo_comms_parameters()


class TPDOconfig(PDOconfig):
  def __init__(self,tab:QWidget,pdo_num:int,pdo_type:str):
    super().__init__(tab,pdo_num,pdo_type)

    self.triggers = [0]*14
    self.analog_thresholds = [0]*6

    self.trigger_dict = {
      "OFF"       : 0,
      "Low->High" : 1,
      "High->Low" : 2,
      "Both"      : 3
    }

  def update_tpdo_digital_config(self):
    try:
      combo_box = self.tab.findChild(QComboBox, f"comboBox_TPDO{self.pdo_num}_DIN1").currentText()
      self.triggers[_TRIGGER_MODE_DIN_1] = self.trigger_dict[combo_box]
      combo_box = self.tab.findChild(QComboBox, f"comboBox_TPDO{self.pdo_num}_DIN2").currentText()
      self.triggers[_TRIGGER_MODE_DIN_2] = self.trigger_dict[combo_box]
      combo_box = self.tab.findChild(QComboBox, f"comboBox_TPDO{self.pdo_num}_DIN3").currentText()
      self.triggers[_TRIGGER_MODE_DIN_3] = self.trigger_dict[combo_box]
      combo_box = self.tab.findChild(QComboBox, f"comboBox_TPDO{self.pdo_num}_DIN4").currentText()
      self.triggers[_TRIGGER_MODE_DIN_4] = self.trigger_dict[combo_box]
      combo_box = self.tab.findChild(QComboBox, f"comboBox_TPDO{self.pdo_num}_DIN5").currentText()
      self.triggers[_TRIGGER_MODE_DIN_5] = self.trigger_dict[combo_box]
      combo_box = self.tab.findChild(QComboBox, f"comboBox_TPDO{self.pdo_num}_DIN6").currentText()
      self.triggers[_TRIGGER_MODE_DIN_6] = self.trigger_dict[combo_box]
      combo_box = self.tab.findChild(QComboBox, f"comboBox_TPDO{self.pdo_num}_DIN7").currentText()
      self.triggers[_TRIGGER_MODE_DIN_7] = self.trigger_dict[combo_box]
      combo_box = self.tab.findChild(QComboBox, f"comboBox_TPDO{self.pdo_num}_DIN8").currentText()
      self.triggers[_TRIGGER_MODE_DIN_8] = self.trigger_dict[combo_box]
    except Exception as e:
      print (f"TPDO{self.pdo_num} APPLY Digital reads: ",e)

  def update_tpdo_analog_config(self):
    try:
        #Modes
      combo_box = self.tab.findChild(QComboBox, f"comboBox_TPDO{self.pdo_num}_GYROX").currentText()
      self.triggers[_TRIGGER_MODE_GYRO_X] = self.trigger_dict[combo_box]
      combo_box = self.tab.findChild(QComboBox, f"comboBox_TPDO{self.pdo_num}_GYROY").currentText()
      self.triggers[_TRIGGER_MODE_GYRO_Y] = self.trigger_dict[combo_box]
      combo_box = self.tab.findChild(QComboBox, f"comboBox_TPDO{self.pdo_num}_GYROZ").currentText()
      self.triggers[_TRIGGER_MODE_GYRO_Z] = self.trigger_dict[combo_box]
      combo_box = self.tab.findChild(QComboBox, f"comboBox_TPDO{self.pdo_num}_ACCELX").currentText()
      self.triggers[_TRIGGER_MODE_ACCEL_X] = self.trigger_dict[combo_box]
      combo_box = self.tab.findChild(QComboBox, f"comboBox_TPDO{self.pdo_num}_ACCELY").currentText()
      self.triggers[_TRIGGER_MODE_ACCEL_Y] = self.trigger_dict[combo_box]
      combo_box = self.tab.findChild(QComboBox, f"comboBox_TPDO{self.pdo_num}_ACCELZ").currentText()
      self.triggers[_TRIGGER_MODE_ACCEL_Z] = self.trigger_dict[combo_box]
        
      # Read all PDO data into the correct objects (thresholds)
      line_edit = int(self.tab.findChild(QLineEdit, f"TPDO{self.pdo_num}_Gyro_X_threshold").text())
      self.analog_thresholds[_ANALOG_THRESHOLD_GYRO_X] = line_edit
      line_edit = int(self.tab.findChild(QLineEdit, f"TPDO{self.pdo_num}_Gyro_Y_threshold").text())
      self.analog_thresholds[_ANALOG_THRESHOLD_GYRO_Y] = line_edit
      line_edit = int(self.tab.findChild(QLineEdit, f"TPDO{self.pdo_num}_Gyro_Z_threshold").text())
      self.analog_thresholds[_ANALOG_THRESHOLD_GYRO_Z] = line_edit
      line_edit = int(self.tab.findChild(QLineEdit, f"TPDO{self.pdo_num}_Accel_X_threshold").text())
      self.analog_thresholds[_ANALOG_THRESHOLD_ACCEL_X] = line_edit
      line_edit = int(self.tab.findChild(QLineEdit, f"TPDO{self.pdo_num}_Accel_Y_threshold").text())
      self.analog_thresholds[_ANALOG_THRESHOLD_ACCEL_Y] = line_edit
      line_edit = int(self.tab.findChild(QLineEdit, f"TPDO{self.pdo_num}_Accel_Z_threshold").text())
      self.analog_thresholds[_ANALOG_THRESHOLD_ACCEL_Z] = line_edit
    except Exception as e:
      print (f"TPDO{self.pdo_num} APPLY Analog reads: ",e)

  def update_tpdo_config(self):
    self.update_general_pdo_config()
    self.update_tpdo_analog_config()
    self.update_tpdo_digital_config()
  


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
        # Use the custom ComboBox
      self.ui.comboBoxConnections = CustomComboBox(self.ui.comboBoxConnections)
      self.ui.comboBoxBaudRates.addItems(["1000","500","250","125","62.5"])
      self.check_boxes_states = 0
      # Connect signals (e.g., buttons or checkboxes)
      self.setup_connections()
      self.connect_existing_checkboxes()

      self.tpdo1 = TPDOconfig(self.ui.TPDO_tab_widget,1,"T")
      self.tpdo2 = TPDOconfig(self.ui.TPDO_tab_widget,2,"T")
      self.tpdo3 = TPDOconfig(self.ui.TPDO_tab_widget,3,"T")
      self.tpdo4 = TPDOconfig(self.ui.TPDO_tab_widget,4,"T")
      
      self.rpdo1 = PDOconfig(self.ui.RPDO_tab_widget,1,"R")
      self.rpdo2 = PDOconfig(self.ui.RPDO_tab_widget,2,"R")
      self.rpdo3 = PDOconfig(self.ui.RPDO_tab_widget,3,"R")
      self.rpdo4 = PDOconfig(self.ui.RPDO_tab_widget,4,"R")


        # Set up the timer to call update_label every 100ms
      self.timer = QTimer(self)
      self.timer.timeout.connect(self.update_periodic_data)
      self.timer.start(100)  # 100 ms interval

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
          if (state == 2):
            self.check_boxes_states |= 1 << position
          else:
            self.check_boxes_states &= (0xFF ^(1 << position))
          
          print(f"{checkbox.text()} changed to {state} {'Checked' if state == 2 else 'Unchecked'}")


    def setup_connections(self):
      # Example: Connect a button to a method
      self.ui.ButtonConnect.clicked.connect(self.handle_connect_button_click)
      self.ui.ButtonOutput.clicked.connect(self.handle_set_outputs_button_click)
      self.ui.ButtonNMTStart.clicked.connect(self.can_handler.start_can_node)
      self.ui.ButtonNMTStop.clicked.connect(self.can_handler.stop_can_node)
      self.ui.ButtonNMTRestart.clicked.connect(self.can_handler.restart_can_node)
      self.ui.ButtonNMTResetComms.clicked.connect(self.can_handler.reset_comms_can_node)

      self.ui.PDO_apply_button.clicked.connect(self.handle_pdo_apply_button_click)
      
      # Example: Connect a checkbox to a method
      self.ui.checkBoxOut1.stateChanged.connect(self.handle_checkbox_state_change)

    def handle_pdo_apply_button_click(self):
      self.tpdo1.update_tpdo_config()
      self.tpdo2.update_tpdo_config()
      self.tpdo3.update_tpdo_config()
      self.tpdo4.update_tpdo_config()

      self.rpdo1.update_general_pdo_config()
      self.rpdo2.update_general_pdo_config()
      self.rpdo3.update_general_pdo_config()
      self.rpdo4.update_general_pdo_config()
      
        # Send output update to the device
      # self.can_handler.upate_pdo_registers()
      
    def handle_connect_button_click(self):
      print("Button clicked!")
      device = self.ui.comboBoxConnections.currentText()
      # need to handle only numbers
      self.can_handler.node_id = int(self.ui.TextId.toPlainText())
      
      self.can_handler.baud_rate = float(self.ui.comboBoxBaudRates.currentText())*1000
      print("Connect to ",device)
      print(self.can_handler.connect_device(device,self.can_handler.baud_rate))
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
