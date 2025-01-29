from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt,QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow,QWidget,QCheckBox
from Frontend.src.CAN_IO_GUI import Ui_MainWindow
from Backend.can_handler import CANBusHandler
from Frontend.src.pdo_config import PDOconfig, TPDOconfig
import sys
import os

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

      
      self.can_handler.update_tpdo_config(self.tpdo1)
      self.can_handler.update_tpdo_config(self.tpdo2)
      self.can_handler.update_tpdo_config(self.tpdo3)
      self.can_handler.update_tpdo_config(self.tpdo4)
      
      self.can_handler.update_rpdo_config(self.rpdo1)
      self.can_handler.update_rpdo_config(self.rpdo2)
      self.can_handler.update_rpdo_config(self.rpdo3)
      self.can_handler.update_rpdo_config(self.rpdo4)
      
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
