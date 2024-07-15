import os
from pathlib import Path
from werkzeug.utils import secure_filename
from collections import Counter

from flask import Flask, render_template, redirect, request

from PIL import Image
import numpy as np


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "static" / "media"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# RGBをヘックスコードに変換する関数
def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))


@app.route('/')
def index():
    files = os.listdir(UPLOAD_FOLDER)
    if files:
        img_path = "media/" + files[0]

        img = Image.open('static/' + img_path)
        colors = analyze_image(img)
        return render_template('index.html', image=img_path, colors=colors)
    return render_template('index.html')

def analyze_image(img):
    img = img.convert('RGB')  # 画像をRGBに変換
    np_img = np.array(img)
    pixels = np_img.reshape(-1, 3)
    counts = Counter(map(tuple, pixels))
    common_colors = counts.most_common(10)
    total_pixels = sum(counts.values())

    hex_colors = []
    for color, count in common_colors:
        hex_color = '#%02x%02x%02x' % color
        percentage = round(count / total_pixels * 100, 5)
        hex_colors.append((hex_color, percentage))

    return hex_colors


@app.route('/upload', methods=['POST'])
def upload_image():

    img = request.files['image']

    if img and allowed_file(img.filename):
        # フォルダ内画像の削除
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

        filename = secure_filename(img.filename)
        try:
            img.save(UPLOAD_FOLDER / filename)  # 画像を保存

        except Exception as e:
            print(f"画像の保存に失敗: {e}")
        return redirect('/')

    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True, port=5003)
