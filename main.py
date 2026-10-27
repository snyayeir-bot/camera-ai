import argparse
import logging
import sys
from PySide6.QtCore import QTimer
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication, QMessageBox
from app.settings_manager import ROOT, Settings
from app.clothing_manager import ClothingManager
from ui.main_window import MainWindow

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--smoke-test', action='store_true', help='Open GUI without webcam and exit after 800 ms')
    parser.add_argument('--screenshot', action='store_true', help='Save startup GUI screenshot (use with smoke test)')
    parser.add_argument('--language', choices=('en','km'), help='Override startup language')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s',
                        handlers=[logging.FileHandler(ROOT/'app.log', encoding='utf-8'), logging.StreamHandler()])
    app = QApplication(sys.argv[:1])
    app.setApplicationName('Khmer AI Virtual Try-On')
    for font in (ROOT/'assets/fonts').glob('*.ttf'):
        QFontDatabase.addApplicationFont(str(font))
    app.setStyleSheet((ROOT/'ui/styles.qss').read_text('utf-8'))
    try:
        settings = Settings()
        if args.language:
            settings.data['language'] = args.language
        catalog = ClothingManager(ROOT/'assets/clothes')
        window = MainWindow(settings, catalog, start_camera=not args.smoke_test)
    except Exception as exc:
        logging.exception('Startup failed')
        if args.smoke_test:
            return 1
        QMessageBox.critical(None, 'Startup error', f'{exc}\n\nRun setup.bat; see README.md for troubleshooting.')
        return 1
    window.show()
    if args.smoke_test:
        if args.screenshot:
            (ROOT/'screenshots').mkdir(exist_ok=True)
            filename = 'welcome-km.png' if settings.data['language']=='km' else 'welcome.png'
            QTimer.singleShot(600, lambda: window.grab().save(str(ROOT/'screenshots'/filename)))
        QTimer.singleShot(800, window.close)
    return app.exec()

if __name__ == '__main__':
    raise SystemExit(main())
