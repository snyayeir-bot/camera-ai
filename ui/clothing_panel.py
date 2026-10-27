from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QListWidget, QListWidgetItem, QListView
from ui.i18n import TEXT, CATEGORIES_KM

class ClothingPanel(QWidget):
    selected = Signal(object)

    def __init__(self, catalog, text):
        super().__init__()
        self.catalog, self.text = catalog, text
        layout = QVBoxLayout(self)
        row = QHBoxLayout()
        row.addWidget(QLabel(text['collection']))
        self.category = QComboBox()
        self.category.addItem(text['all'], '')
        for category in dict.fromkeys(i['category'] for i in catalog.items):
            label = CATEGORIES_KM.get(category,category) if text is TEXT['km'] else category
            self.category.addItem(label, category)
        self.gender = QComboBox()
        self.gender.addItem(text['gender'], '')
        for gender in ('male', 'female', 'unisex'):
            self.gender.addItem(text[gender], gender)
        row.addStretch()
        row.addWidget(self.category)
        row.addWidget(self.gender)
        layout.addLayout(row)
        self.list = QListWidget()
        self.list.setFlow(QListView.LeftToRight)
        self.list.setWrapping(False)
        self.list.setIconSize(QSize(60, 80))
        self.list.setFixedHeight(124)
        self.list.currentItemChanged.connect(self.changed)
        layout.addWidget(self.list)
        self.category.currentIndexChanged.connect(self.populate)
        self.gender.currentIndexChanged.connect(self.populate)
        self.populate()

    def populate(self):
        self.list.clear()
        for outfit in self.catalog.items:
            if self.category.currentData() and outfit['category'] != self.category.currentData():
                continue
            if self.gender.currentData() and outfit['gender'] != self.gender.currentData():
                continue
            item = QListWidgetItem(QIcon(str(self.catalog.root/outfit['thumbnail'])), outfit['name_km'] if self.text is TEXT['km'] else outfit['name'])
            item.setData(Qt.UserRole, outfit)
            item.setSizeHint(QSize(190, 98))
            self.list.addItem(item)
        if self.list.count():
            self.list.setCurrentRow(0)

    def changed(self, current, previous):
        if current:
            self.selected.emit(current.data(Qt.UserRole))

    def step(self, amount):
        if self.list.count():
            self.list.setCurrentRow((self.list.currentRow()+amount)%self.list.count())
