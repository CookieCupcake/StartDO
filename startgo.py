from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QListWidget, QTextEdit, QFileDialog, QVBoxLayout, QHBoxLayout,
    QListWidgetItem, QCheckBox, QDialog, QLineEdit, QDateEdit, QDialogButtonBox, QMessageBox, QMenuBar)
from PyQt5.QtCore import QUrl, QDate, Qt
from PyQt5.QtGui import QDesktopServices, QFont
from PyQt5.QtGui import QIcon
import os
import json

app = QApplication([])

# Ana pencereyi oluştur
window = QWidget()
window.resize(900, 600)
window.setWindowTitle("StartGO")
window.setWindowIcon(QIcon("icon.png"))
window.setStyleSheet("background-color:wheat")



# Default data in case of an empty or invalid file
default_data = {}

# Load data from JSON file
def load_data(filename):
    if not os.path.exists(filename):
        return default_data
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return default_data

# Save data to JSON file
def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(data, file, sort_keys=True, ensure_ascii=True)

# Load initial data
data = load_data("data.json")

# Widget'ları oluştur
font = QFont('Arial', 20)
font2 = QFont('Arial', 15)

text_note_widget = QLabel("Note")
note_widget = QTextEdit()
note_widget.setFont(font2)


text_note_widget.setFont(font)
text_note_widget.setAlignment(Qt.AlignCenter)

text_document_list = QLabel("Documents")
text_document_list.setAlignment(Qt.AlignCenter)
text_document_list.setFont(font)
document_list = QListWidget()
document_list.setFont(font2)
document_list.path = ""
document_button = QPushButton("Get Documents")
document_button.setFont(font2)

text_to_do_list = QLabel("To Do List")
text_to_do_list.setAlignment(Qt.AlignCenter)
text_to_do_list.setFont(font)
to_do_list = QListWidget()
to_do_list.setFont(font2)


add_mission_button = QPushButton("Add")
add_mission_button.setFont(font2)
delete_mission_button = QPushButton("Delete")
delete_mission_button.setFont(font2)
edit_mission_button = QPushButton("Edit")
edit_mission_button.setFont(font2)

widgets=[text_note_widget,note_widget,text_document_list,document_list,document_button,text_to_do_list,to_do_list,add_mission_button,delete_mission_button,edit_mission_button]
def try_colors(color):
    for i in widgets:
        i.setStyleSheet("background-color:"+color+";border-style: outset;border-width:2px ;border-radius: 10px;border-color: bisque")
    
try_colors("beige")
# Fonksiyonları tanımla


def error_screen(text):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setText(text)
    msg.setWindowIcon(QIcon("icon.png"))
    msg.setWindowTitle("ERROR")
    msg.exec_()

def update_checked_status(item):
    mission_name = item.text().split(" Date:")[0][5:]
    if item.checkState() == Qt.Checked:
        data[mission_name]["Checked"] = "Yes"
    else:
        data[mission_name]["Checked"] = "No"
    save_data("data.json", data)

def list_missions():
    to_do_list.clear()
    note_widget.setText("")
    for mission_name in data:
        mission_date = data[mission_name]["Date"]
        item = QListWidgetItem(f"Name:{mission_name} Date:{mission_date}")
        if data[mission_name]["Checked"] == "Yes":
            item.setCheckState(Qt.Checked)
        else:
            item.setCheckState(Qt.Unchecked)
        to_do_list.addItem(item)
    
    to_do_list.itemChanged.connect(update_checked_status)

def show_note():
    if not to_do_list.selectedItems():
        return
    name = to_do_list.selectedItems()[0].text().split(" Date:")[0][5:]
    note_widget.blockSignals(True)
    note_widget.setText(data[name]["Note"])
    note_widget.blockSignals(False)

def save_note():
    if not to_do_list.selectedItems():
        return
    name = to_do_list.selectedItems()[0].text().split(" Date:")[0][5:]
    data[name]["Note"] = note_widget.toPlainText()
    save_data("data.json", data)

class edit_mission_class():
    def __init__(self):
        self.n = to_do_list.selectedItems()[0].text().split(" Date:")[0][5:]

        self.window = QDialog()
        self.window.setWindowIcon(QIcon("icon.png"))
        self.window.setWindowTitle("Edit Mission")

        self.layout = QVBoxLayout()
        
        self.field_mission = QLineEdit(self.n)
        self.field_mission.setPlaceholderText("Mission name")
        
        self.text_date = QLabel("Date")
        self.field_date = QDateEdit()
        self.field_date.setDate(QDate.fromString(data[self.n]["Date"], "dd-MM-yyyy"))
        
        self.btnBox = QDialogButtonBox()
        self.btnBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.btnBox.accepted.connect(self.save)
        self.btnBox.rejected.connect(self.close1)
        
        for i in [self.field_mission, self.text_date, self.field_date, self.btnBox]:
            self.layout.addWidget(i)
        
        self.window.setLayout(self.layout)
        self.window.exec_()

    def save(self):
        if self.field_mission.text() and self.field_date.text() != "":
            data[self.field_mission.text()] = {
                "Date": self.field_date.date().toString("dd-MM-yyyy"),
                "Note":data[self.n]["Note"],
                "Checked":data[self.n]["Checked"]
            }
            if self.field_mission.text() != self.n :
                del data[self.n]


            save_data("data.json", data)
            list_missions()
            self.window.close()
        else:
            error_screen("You entered a missing information!")

    def close1(self):
        self.window.close()

def edit_mission():
    if to_do_list.selectedItems():
        dlg = edit_mission_class()
    else:
        error_screen("Select a mission to edit!")

def open_directory_dialog():
    # Dizin seçim diyalogunu aç
    directory = QFileDialog.getExistingDirectory(window, "Select Directory")
    document_list.path = directory
    if directory:
        # Seçilen dizindeki dosyaları listele
        document_list.clear()
        try:
            for entry in os.listdir(directory):
                path = os.path.join(directory, entry)
                if os.path.isfile(path):  # Sadece dosyaları ekle
                    document_list.addItem(entry)
        except Exception as e:
            document_list.addItem(f"Error: {str(e)}")

def open_selected_file(item):
    # Seçilen dosyanın yolunu al
    file_name = item.text()
    file_path = os.path.join(document_list.path, file_name)

    if os.path.isfile(file_path):
        # Dosyayı varsayılan uygulama ile aç
        QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

def del_mission():
    if to_do_list.selectedItems():

        del data[to_do_list.selectedItems()[0].text().split(" Date:")[0][5:]]
        save_data("data.json", data)
        list_missions()
    else:
        error_screen("Please select mission to delete")

def mission_add():
    dlg = add_mission()

# Classes
class add_mission():
    def __init__(self):
        self.window = QDialog()
        self.window.setWindowIcon(QIcon("icon.png"))
        self.window.setWindowTitle("Add Mission")
        self.layout = QVBoxLayout()
        
        self.field_mission = QLineEdit("")
        self.field_mission.setPlaceholderText("Mission name")
        
        self.text_date = QLabel("Date")
        self.field_date = QDateEdit()
        self.field_date.setDate(QDate.currentDate())
        
        self.btnBox = QDialogButtonBox()
        self.btnBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.btnBox.accepted.connect(self.save)
        self.btnBox.rejected.connect(self.close1)
        
        for i in [self.field_mission, self.text_date, self.field_date, self.btnBox]:
            self.layout.addWidget(i)
        
        self.window.setLayout(self.layout)
        self.window.exec_()

    def save(self):
        if self.field_mission.text() and self.field_date.text() != "":
            if self.field_mission.text() not in data:
                data[self.field_mission.text()] = {
                    "Note": "",
                    "Date": self.field_date.date().toString("dd-MM-yyyy"),
                    "Checked": "No"
                }
                save_data("data.json", data)
                list_missions()
                self.window.close()
            else:
                error_screen("Try a different mission name!")
        else:
            error_screen("You entered a missing information!")

    def close1(self):
        self.window.close()

# Butona tıklama işlevini bağla
document_button.clicked.connect(open_directory_dialog)
add_mission_button.clicked.connect(mission_add)
delete_mission_button.clicked.connect(del_mission)
note_widget.textChanged.connect(save_note)
edit_mission_button.clicked.connect(edit_mission)

# Listeye tıklama işlevini bağla
document_list.itemDoubleClicked.connect(open_selected_file)
to_do_list.itemClicked.connect(show_note)

# Düzenleri oluştur ve widget'ları ekle
main_layout = QHBoxLayout()

col1 = QVBoxLayout()
col1.addWidget(text_note_widget)
col1.addWidget(note_widget)
col1.addWidget(text_document_list)
col1.addWidget(document_list)
col1.addWidget(document_button)

col2 = QVBoxLayout()
col2.addWidget(text_to_do_list)
col2.addWidget(to_do_list)

row1 = QHBoxLayout()
row1.addWidget(add_mission_button)
row1.addWidget(delete_mission_button)
row1.addWidget(edit_mission_button)
col2.addLayout(row1)

main_layout.addLayout(col1)
main_layout.addLayout(col2)

# Düzeni pencereye ayarla
window.setLayout(main_layout)
list_missions()

# Pencereyi göster
window.show()

# Uygulama döngüsünü başlat
app.exec_()
