from PySide6.QtWidgets import (QDialog, QFormLayout, QSpinBox, QDoubleSpinBox,
                              QComboBox, QCheckBox, QLineEdit, QDialogButtonBox)

class SettingsDialog(QDialog):
    def __init__(self, data, text, parent=None):
        super().__init__(parent)
        self.setWindowTitle(text['settings'])
        self.setMinimumWidth(440)
        self.original = data.copy()
        self.fields = {}
        layout = QFormLayout(self)
        for key, label, low, high in [('camera','camera',0,20), ('inference_width','quality',256,1280),
                                       ('hand_interval','hands',1,10)]:
            field = QSpinBox()
            field.setRange(low, high)
            field.setValue(data[key])
            self.fields[key] = field
            layout.addRow(text[label], field)
        self.resolution = QComboBox()
        for w, h in ((640,480), (1280,720), (1920,1080)):
            self.resolution.addItem(f'{w} × {h}', (w,h))
        self.resolution.setCurrentIndex(max(0, self.resolution.findData((data['width'],data['height']))))
        layout.addRow(text['resolution'], self.resolution)
        for key, label in [('mirror','mirror'), ('fullscreen','fullscreen'), ('frame','frame')]:
            field = QCheckBox()
            field.setChecked(data[key])
            self.fields[key] = field
            layout.addRow(text[label], field)
        for key, label, low, high in [('sensitivity','sensitivity',.2,.95), ('clothing_scale','scale',.7,1.5)]:
            field = QDoubleSpinBox()
            field.setRange(low,high)
            field.setSingleStep(.05)
            field.setValue(data[key])
            self.fields[key] = field
            layout.addRow(text[label], field)
        language = QComboBox()
        language.addItem('English', 'en')
        language.addItem('ខ្មែរ', 'km')
        language.setCurrentIndex(language.findData(data['language']))
        self.fields['language'] = language
        layout.addRow(text['language'], language)
        directory = QLineEdit(data['photo_dir'])
        self.fields['photo_dir'] = directory
        layout.addRow(text['directory'], directory)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText(text['apply'])
        buttons.button(QDialogButtonBox.Cancel).setText(text['cancel'])
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def values(self):
        data = self.original.copy()
        for key, field in self.fields.items():
            if isinstance(field, QCheckBox):
                data[key] = field.isChecked()
            elif isinstance(field, QComboBox):
                data[key] = field.currentData()
            elif isinstance(field, QLineEdit):
                data[key] = field.text()
            else:
                data[key] = field.value()
        data['width'], data['height'] = self.resolution.currentData()
        return data
