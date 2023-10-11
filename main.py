from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QColorDialog, QLabel, QMenu, QGridLayout, QAction
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt, QStandardPaths
import sys
import pickle
import os

class ColorPaletteApp(QMainWindow):
	def __init__(self):
		super().__init__()

		self.color_palette = []
		self.color_widgets = []

		self.initUI()

		for i in self.load_session_data():
			self.color_palette.append(QColor(i))
			self.add_color_to_ui(QColor(i))
		

	def initUI(self):
		self.setWindowTitle("Color Palette")
		self.setGeometry(100, 100, 400, 400)

		self.central_widget = QWidget(self)
		self.setCentralWidget(self.central_widget)

		self.layout = QVBoxLayout(self.central_widget)
		self.color_layout = QGridLayout()

		self.add_color_button = QPushButton("+")
		self.add_color_button.setMaximumWidth(50)
		self.add_color_button.setMaximumHeight(50)
		self.add_color_button.setStyleSheet("font-size: 20px;")

		self.add_color_button.clicked.connect(self.show_color_dialog)

		self.layout.addWidget(self.add_color_button)
		self.layout.addLayout(self.color_layout)
			 

	def show_color_dialog(self):
		color_dialog = QColorDialog(self)
		color = color_dialog.getColor()

		if color.isValid():
			self.color_palette.append(color)
			self.add_color_to_ui(color)

	def add_color_to_ui(self, color):
		color_widget = QWidget()

		color_block = QLabel()
		color_block.setMaximumSize(200, 200)
		color_block.setMinimumSize(100, 100)
		color_block.setStyleSheet(f"background-color: {color.name()};")

		hex_label = QLabel(color.name())
		hex_label.setStyleSheet("font-size: 20px;")

		color_layout = QVBoxLayout()
		color_layout.addWidget(hex_label)
		color_layout.addWidget(color_block)
		color_widget.setLayout(color_layout)

		row = (len(self.color_palette) - 1) // 2
		col = (len(self.color_palette) - 1) % 2

		self.color_layout.addWidget(color_widget, row, col)
		self.color_widgets.append(color_widget)

		def mousePressEvent(event):
			if event.button() == Qt.RightButton:
				context_menu = QMenu(self)
				hex_action = context_menu.addAction("Copy HEX")
				rgb_action = context_menu.addAction("Copy RGBA")
				remove_action = context_menu.addAction("Remove Color")

				hex_action.triggered.connect(lambda: self.copy_to_clipboard(color.name()))
				rgb_action.triggered.connect(lambda: self.copy_to_clipboard(str(color.getRgb())))
				remove_action.triggered.connect(lambda: self.remove_color(color, color_widget))

				context_menu.exec_(event.globalPos())

		color_widget.mousePressEvent = mousePressEvent

	def copy_to_clipboard(self, value):
		clipboard = QApplication.clipboard()
		clipboard.setText(value)

	def remove_color(self, color, color_widget):
		temp_palette = []
		temp_widgets = []

		self.color_palette.remove(color)
		self.color_widgets.remove(color_widget)
		color_widget.deleteLater()

		temp_palette.extend(self.color_palette)
		temp_widgets.extend(self.color_widgets)

		self.color_palette.clear()
		self.color_widgets.clear()

		for i in reversed(range(self.color_layout.count())):
			widget = self.color_layout.itemAt(i).widget()
			if widget:
				widget.deleteLater()

		for color, widget in zip(temp_palette, temp_widgets):
			self.color_palette.append(color)
			self.add_color_to_ui(color)


	def save_session_data(self, data):
		with open('session_data.pkl', 'wb') as f:
			pickle.dump(data, f)


	@staticmethod
	def get_session_data_path():
		documents_dir = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)

		app_data_dir = os.path.join(documents_dir, "ColorPalette_data")

		os.makedirs(app_data_dir, exist_ok=True)

		return os.path.join(app_data_dir, "session_data.pkl")

	def save_session_data(self, data):
		session_data_path = self.get_session_data_path()
		with open(session_data_path, 'wb') as f:
			pickle.dump(data, f)

	@staticmethod
	def load_session_data():
		session_data_path = ColorPaletteApp.get_session_data_path()
		try:
			with open(session_data_path, 'rb') as f:
				data = pickle.load(f)
				return data
		except FileNotFoundError:
			return []

	def closeEvent(self, event):
		self.save_session_data(self.color_palette)
		event.accept()

def main():
	app = QApplication(sys.argv)
	main_window = ColorPaletteApp()
	main_window.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()
