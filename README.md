# WORK IN PROGRESS!! / まだ作業中！！
# Simple Python RPA Framework / シンプルなPythonRPAフレームワーク

A lightweight Python framework for RPA (Robotic Process Automation) with OCR and template matching.
OCR (Optical Character Recognition) supports both Japanese and English.

日本語と英語のOCRに対応した、軽量なPython製RPA（ロボティック・プロセス・オートメーション）フレームワークです。画像テンプレートマッチングも可能です。

---

## Features / 主な機能

- OCR (Japanese & English) / OCR（日本語・英語対応）
- Template matching / 画像テンプレートマッチング
- Mouse & keyboard automation / マウス・キーボード自動化
- Clipboard access / クリップボード操作
- Wait for presence (image/text) / 画像やテキストの出現待ち
- Scroll & click actions / スクロール・クリック操作

---

## Installation / インストール

```bash
pip install opencv-python numpy mss easyocr torch pynput pyperclip
```

---

## Usage Example / 使い方例

```python
import PyAutomate as pa

# Move mouse to coordinates / マウスを座標に移動
pa.hover(100, 200)

# Type text / テキスト入力
pa.type("Hello, world!")

# Click on an image on the screen / 画面上の画像をクリック
pa.click("img/sample.png")

# OCR on a screenshot / スクリーンショットでOCR
text_data = pa.ocr(pa.screenshot()[0])
print(text_data['text'])
```

---

## Dependencies / 依存パッケージ

- opencv-python
- numpy
- mss
- easyocr
- torch
- pynput
- pyperclip

---

## License / ライセンス

MIT License

---

## Notes / 注意事項

- Requires Python 3.7 or later. / Python 3.7以降が必要です。
- For GPU OCR, CUDA-compatible GPU and drivers are required. / GPU OCRにはCUDA対応GPUとドライバが必要です。

---

## Author / 作者

[Fuwakami Mana]
