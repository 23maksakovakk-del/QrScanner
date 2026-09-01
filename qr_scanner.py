# qr_scanner.py
# Версия на Python с использованием OpenCV и pyzbar

import sys
import cv2
import pyzbar.pyzbar as pyzbar
import argparse
import time
import os
import platform
from datetime import datetime

try:
    import pyperclip
    HAS_CLIPBOARD = True
except ImportError:
    HAS_CLIPBOARD = False

class QRScanner:
    def __init__(self, camera_id=0, use_flash=False, copy_to_clipboard=False, output_file=None, gui=True):
        self.camera_id = camera_id
        self.use_flash = use_flash
        self.copy_to_clipboard = copy_to_clipboard
        self.output_file = output_file
        self.gui = gui
        self.cap = None
        self.results = []

    def _toggle_flash(self, on):
        """Включить/выключить фонарик (вспышку) на камере."""
        if not self.cap:
            return
        # Для OpenCV на некоторых платформах доступно управление вспышкой
        # Параметр CAP_PROP_AUTOFOCUS и другие
        try:
            # Попытка включить вспышку через свойства камеры
            if on:
                self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)  # отключаем автофокус
                # Установка яркости/экспозиции для имитации вспышки не работает
                # Используем системные вызовы для Android/iOS? В демо просто имитируем
                print("💡 Фонарик включён (имитация)")
            else:
                print("💡 Фонарик выключен")
        except Exception as e:
            print(f"Не удалось управлять фонариком: {e}")

    def _copy_to_clipboard(self, text):
        if HAS_CLIPBOARD:
            pyperclip.copy(text)
            print("📋 Результат скопирован в буфер обмена")
        else:
            print("⚠️  pyperclip не установлен, копирование невозможно")

    def _save_result(self, text):
        if self.output_file:
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now().isoformat()} - {text}\n")
            print(f"💾 Результат сохранён в {self.output_file}")

    def _process_frame(self, frame):
        """Обрабатывает кадр, ищет QR-коды."""
        # Декодируем штрих-коды
        barcodes = pyzbar.decode(frame)
        for barcode in barcodes:
            # Извлекаем данные
            data = barcode.data.decode('utf-8')
            if data not in self.results:
                self.results.append(data)
                print(f"✅ Найден QR-код: {data}")
                if self.copy_to_clipboard:
                    self._copy_to_clipboard(data)
                if self.output_file:
                    self._save_result(data)
        return barcodes

    def _draw_barcode(self, frame, barcode):
        """Рисует прямоугольник вокруг QR-кода."""
        (x, y, w, h) = barcode.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        # Текст с данными
        data = barcode.data.decode('utf-8')
        cv2.putText(frame, data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    def scan_once(self):
        """Сканирует один QR-код и завершает работу."""
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            print("❌ Не удалось открыть камеру")
            return

        if self.use_flash:
            self._toggle_flash(True)

        print("🔍 Сканирование одного QR-кода... Нажмите ESC для отмены")
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            barcodes = self._process_frame(frame)
            if barcodes:
                # Рисуем рамку
                for barcode in barcodes:
                    self._draw_barcode(frame, barcode)
                if self.gui:
                    cv2.imshow("QR Scanner", frame)
                cv2.waitKey(500)
                break

            if self.gui:
                cv2.imshow("QR Scanner", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break

        if self.use_flash:
            self._toggle_flash(False)

        self.cap.release()
        if self.gui:
            cv2.destroyAllWindows()

    def scan_continuous(self):
        """Непрерывное сканирование QR-кодов."""
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            print("❌ Не удалось открыть камеру")
            return

        if self.use_flash:
            self._toggle_flash(True)

        print("🔍 Непрерывное сканирование... Нажмите ESC для выхода")
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            barcodes = self._process_frame(frame)
            for barcode in barcodes:
                self._draw_barcode(frame, barcode)

            if self.gui:
                cv2.imshow("QR Scanner", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break

        if self.use_flash:
            self._toggle_flash(False)

        self.cap.release()
        if self.gui:
            cv2.destroyAllWindows()

    def flash(self, duration):
        """Включает фонарик на указанное время."""
        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            print("❌ Не удалось открыть камеру")
            return
        self._toggle_flash(True)
        time.sleep(duration)
        self._toggle_flash(False)
        self.cap.release()

def main():
    parser = argparse.ArgumentParser(description='QR Scanner (Python)')
    parser.add_argument('command', nargs='?', default='scan',
                        choices=['scan', 'once', 'flash'],
                        help='Команда: scan (непрерывно), once (один раз), flash (фонарик)')
    parser.add_argument('duration', nargs='?', type=int, default=5,
                        help='Длительность вспышки (сек) для команды flash')
    parser.add_argument('-c', '--camera', type=int, default=0, help='ID камеры')
    parser.add_argument('-o', '--output', help='Файл для сохранения результатов')
    parser.add_argument('--copy', action='store_true', help='Копировать в буфер обмена')
    parser.add_argument('--flash', action='store_true', help='Включить фонарик при сканировании')
    parser.add_argument('--no-gui', action='store_true', help='Отключить графическое окно')
    args = parser.parse_args()

    scanner = QRScanner(
        camera_id=args.camera,
        use_flash=args.flash,
        copy_to_clipboard=args.copy,
        output_file=args.output,
        gui=not args.no_gui
    )

    if args.command == 'flash':
        scanner.flash(args.duration or 5)
    elif args.command == 'once':
        scanner.scan_once()
    else:
        scanner.scan_continuous()

if __name__ == '__main__':
    main()
