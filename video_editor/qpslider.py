from PyQt5.QtWidgets import QProgressBar, QDialogButtonBox, QDialog, QInputDialog, QProgressBar, QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTableWidget, QTableWidgetItem, QListWidget, QListWidgetItem, QSlider
from PyQt5.QtCore import Qt


class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.mainUI()
        self.setLayout()
        self.setWindowTitle("List App")
        self.setFixedSize(500, 300)
        self.setCentralWidget(self.setWidget)

    def mainUI(self):
        self.list = QListWidget()
        self.buttonAddItem = QPushButton("Add Item")
        self.buttonRemoveItem = QPushButton("Remove Item")
        self.buttonUpdateItem = QPushButton("update Item")
        self.buttonClearAllItem = QPushButton("clear all Item")
        self.buttonDuplicateItem = QPushButton("duplicate Item")

        # logic for progresss Bar
        self.buttonAddItem.clicked.connect(self.setInput)
        self.buttonRemoveItem.clicked.connect(self.setRemove)
        self.buttonClearAllItem.clicked.connect(self.setClear)
        self.buttonUpdateItem.clicked.connect(self.setUpdate)

        # logic for slider
        self.buttonDuplicateItem.clicked.connect(self.setDuplicate)

        self.slider = QSlider(Qt.Horizontal)
        self.progressbar = QProgressBar()

    def setLayout(self):
        self.layoutList = QVBoxLayout()
        self.layoutList.addWidget(self.list)
        self.layoutList.addWidget(self.buttonAddItem)
        self.layoutList.addWidget(self.buttonRemoveItem)
        self.layoutList.addWidget(self.buttonUpdateItem)
        self.layoutList.addWidget(self.buttonClearAllItem)
        self.layoutList.addWidget(self.buttonDuplicateItem)
        self.layoutList.addWidget(self.slider)
        self.layoutList.addWidget(self.progressbar)

        self.setWidget = QWidget()
        self.setWidget.setLayout(self.layoutList)

    def setDialog(self):

        self.dialog = QDialog()
        self.dialog.setFixedSize(400, 200)
        self.dialog.setWindowTitle("Custom Dialog Box")

        self.labelDialog = QLabel("custom label")
        self.button = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(self.button)
        self.buttonBox.accepted.connect(self.dialog.accept)

        self.layoutDialog = QVBoxLayout()
        self.layoutDialog.addWidget(self.labelDialog)
        self.layoutDialog.addWidget(self.buttonBox)

        self.dialog.setLayout(self.layoutDialog)
        self.dialog.exec_()

    # logic dialog

    def setInput(self):
        self.inputDialog, ok = QInputDialog.getText(
            self, "Add to List Item", "Enter Input")
        if ok == True:
            if self.inputDialog != "":
                self.add = QListWidgetItem(self.inputDialog, self.list)
                self.list.addItem(self.add)
                self.progressbar.setValue(self.list.count())
                print(f"check input dialog : {self.inputDialog}")
        print(ok)

    def setRemove(self):
        listdata_items = self.list.selectedItems()
        if not listdata_items:
            return
        for item in listdata_items:
            self.list.takeItem(self.list.row(item))
            self.progressbar.setValue(self.list.count())

    def setClear(self):
        self.list.clear()
        self.progressbar.setValue(self.list.count())

    def setUpdate(self):
        dialog_update = QInputDialog()
        listdata_selected = self.list.selectedItems()
        index = ['%s' % (i.text()) for i in listdata_selected]

        result, ok = dialog_update.getText(
            self, "Update List Item", "Update List", text=index[0])

        if ok == True and result != "":
            for item in listdata_selected:
                self.list.item(
                    self.list.row(item)).setText(result)
        self.progressbar.setValue(self.list.count())

    def setDuplicate(self):
        range_itemselected = self.valuesitem_slider()
        listdata_selected = ['%s' % (i.text())
                             for i in self.list.selectedItems()]
        for x in range(range_itemselected):
            QListWidgetItem(listdata_selected[0], self.list)
            self.progressbar.setValue(self.list.count())
        self.progressbar.setValue(self.list.count())

    def valuesitem_slider(self):
        return self.slider.value()


if __name__ == "__main__":
    app = QApplication([])
    window = MyApp()
    window.show()
    app.exec_()