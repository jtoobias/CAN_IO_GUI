from PyQt6.QtWidgets import QApplication, QMainWindow,QWidget,\
    QVBoxLayout, QCheckBox, QComboBox, QTableWidget, QSpinBox,QLineEdit

def get_value_from_text_box(text:str):
	try:
			# Try converting to integer first
		num = int(text)
		return num
	except ValueError:
		try:
				# If integer conversion fails, try float
			num = float(text)
			return num
		except ValueError:
			return None 

class PDOconfig():
   
	def __init__(self,tab:QWidget,pdo_num:int,pdo_type:str):
		# self.canh = canh
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
					self.mapped_indices[row:-1] = [-1] * (len(self.mapped_indices) - row)
					break
				print(f"{self.pdo_type}PDO{self.pdo_num}: Mapped indices: {hex(value)}")
				self.mapped_indices[row] = value
		except Exception as e:
			print (f"{self.pdo_type}PDO{self.pdo_num} APPLY Mapped Indices: ",e)

	def update_pdo_comms_parameters(self):
		try:
			value = get_value_from_text_box(self.tab.findChild(QLineEdit, f"COB_ID_box_{self.pdo_type}PDO{self.pdo_num}").text())
			if (value != None): self.cob_id = int(value)
			else: self.cob_id = -1
			value = get_value_from_text_box(self.tab.findChild(QLineEdit, f"Inhibit_time_box_{self.pdo_type}PDO{self.pdo_num}").text())
			if (value != None): self.inhibit_time = int(value)
			else: self.inhibit_time = -1
			value = get_value_from_text_box(self.tab.findChild(QLineEdit, f"Transmit_period_box_{self.pdo_type}PDO{self.pdo_num}").text())
			if (value != None): self.transmit_period = int(value)
			else: self.transmit_period = -1
			self.transmission_type_value = int(self.tab.findChild(QSpinBox, f"spinBox_{self.pdo_type}PDO{self.pdo_num}").value())
		except Exception as e:
			print (f"{self.pdo_type}PDO{self.pdo_num} APPLY Comms Params: ",e)


	def update_general_pdo_config(self):
		self.update_pdo_mapped_indices()
		self.update_pdo_comms_parameters()


class TPDOconfig(PDOconfig):

	__ANALOG_THRESHOLD_GYRO_X = 0
	__ANALOG_THRESHOLD_GYRO_Y = 1
	__ANALOG_THRESHOLD_GYRO_Z = 2
	__ANALOG_THRESHOLD_ACCEL_X = 3
	__ANALOG_THRESHOLD_ACCEL_Y = 4
	__ANALOG_THRESHOLD_ACCEL_Z = 5

	__TRIGGER_MODE_DIN_1 = 0
	__TRIGGER_MODE_DIN_2 = 1
	__TRIGGER_MODE_DIN_3 = 2
	__TRIGGER_MODE_DIN_4 = 3
	__TRIGGER_MODE_DIN_5 = 4
	__TRIGGER_MODE_DIN_6 = 5
	__TRIGGER_MODE_DIN_7 = 6
	__TRIGGER_MODE_DIN_8 = 7
	__TRIGGER_MODE_GYRO_X = 8
	__TRIGGER_MODE_GYRO_Y = 9
	__TRIGGER_MODE_GYRO_Z = 10
	__TRIGGER_MODE_ACCEL_X = 11
	__TRIGGER_MODE_ACCEL_Y = 12
	__TRIGGER_MODE_ACCEL_Z = 13

	def __init__(self,tab:QWidget,pdo_num:int,pdo_type:str):
		super().__init__(tab,pdo_num,pdo_type)

		self.triggers = [0]*14
		self.analog_thresholds = [None]*6

		self.trigger_dict = {
			"OFF"       : 0,
			"Low->High" : 1,
			"High->Low" : 2,
			"Both"      : 3
		}

	def update_tpdo_digital_config(self):
		try:
			combo_box = self.tab.findChild(QComboBox, f"comboBox_TPDO{self.pdo_num}_IN1").currentText()
			self.triggers[self.__TRIGGER_MODE_DIN_1] = self.trigger_dict[combo_box]
			print (self.triggers[self.__TRIGGER_MODE_DIN_1])
			combo_box = self.tab.findChild(QComboBox, f"comboBox_TPDO{self.pdo_num}_IN2").currentText()
			self.triggers[self.__TRIGGER_MODE_DIN_2] = self.trigger_dict[combo_box]
			combo_box = self.tab.findChild(QComboBox, f"comboBox_TPDO{self.pdo_num}_IN3").currentText()
			self.triggers[self.__TRIGGER_MODE_DIN_3] = self.trigger_dict[combo_box]
			combo_box = self.tab.findChild(QComboBox, f"comboBox_TPDO{self.pdo_num}_IN4").currentText()
			self.triggers[self.__TRIGGER_MODE_DIN_4] = self.trigger_dict[combo_box]
			combo_box = self.tab.findChild(QComboBox, f"comboBox_TPDO{self.pdo_num}_IN5").currentText()
			self.triggers[self.__TRIGGER_MODE_DIN_5] = self.trigger_dict[combo_box]
			combo_box = self.tab.findChild(QComboBox, f"comboBox_TPDO{self.pdo_num}_IN6").currentText()
			self.triggers[self.__TRIGGER_MODE_DIN_6] = self.trigger_dict[combo_box]
			combo_box = self.tab.findChild(QComboBox, f"comboBox_TPDO{self.pdo_num}_IN7").currentText()
			self.triggers[self.__TRIGGER_MODE_DIN_7] = self.trigger_dict[combo_box]
			combo_box = self.tab.findChild(QComboBox, f"comboBox_TPDO{self.pdo_num}_IN8").currentText()
			self.triggers[self.__TRIGGER_MODE_DIN_8] = self.trigger_dict[combo_box]
			
			print (f"TPDO{self.pdo_num} Triggers: {self.triggers}")
			print (f"TPDO{self.pdo_num} Analog Thresholds: {self.analog_thresholds}")
		except Exception as e:
			print (f"TPDO{self.pdo_num} APPLY Digital reads: ",e)

	def update_tpdo_analog_config(self):
		try:
				#Modes
			combo_box = self.tab.findChild(QComboBox, f"comboBox_TPDO{self.pdo_num}_GYROX").currentText()
			self.triggers[self.__TRIGGER_MODE_GYRO_X] = self.trigger_dict[combo_box]
			combo_box = self.tab.findChild(QComboBox, f"comboBox_TPDO{self.pdo_num}_GYROY").currentText()
			self.triggers[self.__TRIGGER_MODE_GYRO_Y] = self.trigger_dict[combo_box]
			combo_box = self.tab.findChild(QComboBox, f"comboBox_TPDO{self.pdo_num}_GYROZ").currentText()
			self.triggers[self.__TRIGGER_MODE_GYRO_Z] = self.trigger_dict[combo_box]
			combo_box = self.tab.findChild(QComboBox, f"comboBox_TPDO{self.pdo_num}_ACCELX").currentText()
			self.triggers[self.__TRIGGER_MODE_ACCEL_X] = self.trigger_dict[combo_box]
			combo_box = self.tab.findChild(QComboBox, f"comboBox_TPDO{self.pdo_num}_ACCELY").currentText()
			self.triggers[self.__TRIGGER_MODE_ACCEL_Y] = self.trigger_dict[combo_box]
			combo_box = self.tab.findChild(QComboBox, f"comboBox_TPDO{self.pdo_num}_ACCELZ").currentText()
			self.triggers[self.__TRIGGER_MODE_ACCEL_Z] = self.trigger_dict[combo_box]
				
			# Read all PDO data into the correct objects (thresholds)
			line_edit = get_value_from_text_box(self.tab.findChild(QLineEdit, f"TPDO{self.pdo_num}_Gyro_X_threshold").text())
			self.analog_thresholds[self.__ANALOG_THRESHOLD_GYRO_X] = line_edit
			line_edit = get_value_from_text_box(self.tab.findChild(QLineEdit, f"TPDO{self.pdo_num}_Gyro_Y_threshold").text())
			self.analog_thresholds[self.__ANALOG_THRESHOLD_GYRO_Y] = line_edit
			line_edit = get_value_from_text_box(self.tab.findChild(QLineEdit, f"TPDO{self.pdo_num}_Gyro_Z_threshold").text())
			self.analog_thresholds[self.__ANALOG_THRESHOLD_GYRO_Z] = line_edit
			line_edit = get_value_from_text_box(self.tab.findChild(QLineEdit, f"TPDO{self.pdo_num}_Accel_X_threshold").text())
			self.analog_thresholds[self.__ANALOG_THRESHOLD_ACCEL_X] = line_edit
			line_edit = get_value_from_text_box(self.tab.findChild(QLineEdit, f"TPDO{self.pdo_num}_Accel_Y_threshold").text())
			self.analog_thresholds[self.__ANALOG_THRESHOLD_ACCEL_Y] = line_edit
			line_edit = get_value_from_text_box(self.tab.findChild(QLineEdit, f"TPDO{self.pdo_num}_Accel_Z_threshold").text())
			self.analog_thresholds[self.__ANALOG_THRESHOLD_ACCEL_Z] = line_edit
			
		except Exception as e:
			print (f"TPDO{self.pdo_num} APPLY Analog reads: ",e)

	def update_tpdo_config(self):
		self.update_general_pdo_config()
		self.update_tpdo_analog_config()
		self.update_tpdo_digital_config()
