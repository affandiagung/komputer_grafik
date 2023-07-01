import os
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from PIL import Image


# token_30hari = "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"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Konfigurasi pesan flash
app.secret_key = 'supersecretkey'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def crop_image(image, size, position):
    width, height = image.size

    # Hitung posisi crop
    if position == 'top_left':
        left, upper, right, lower = 0, 0, size, size
    elif position == 'top_center':
        left, upper, right, lower = (width-size)//2, 0, (width+size)//2, size
    elif position == 'top_right':
        left, upper, right, lower = width-size, 0, width, size
    elif position == 'center_left':
        left, upper, right, lower = 0, (height-size)//2, size, (height+size)//2
    elif position == 'center':
        left, upper, right, lower = (width-size)//2, (height-size)//2, (width+size)//2, (height+size)//2
    elif position == 'center_right':
        left, upper, right, lower = width-size, (height-size)//2, width, (height+size)//2
    elif position == 'bottom_left':
        left, upper, right, lower = 0, height-size, size, height
    elif position == 'bottom_center':
        left, upper, right, lower = (width-size)//2, height-size, (width+size)//2, height
    elif position == 'bottom_right':
        left, upper, right, lower = width-size, height-size, width, height

    # Crop gambar
    cropped_image = image.crop((left, upper, right, lower))

    return cropped_image

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Cek apakah file diupload
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        print(file)
        # Cek apakah file yang diunggah sesuai format
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # Simpan file yang diunggah
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            return redirect(url_for('crop_image_route', filename=filename))
        else:
            flash('Invalid file format')
            return redirect(request.url)

    return render_template('index.html')

@app.route('/crop/<filename>', methods=['GET', 'POST'])
def crop_image_route(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image = Image.open(file_path)

    if request.method == 'POST':
        # Validasi ukuran crop
        size = int(request.form['size'])
        if size > image.width or size > image.height:
            flash('Crop size is larger than image size')
            return redirect(request.url)

        # Proses crop gambar
        position = request.form['position']
        cropped_image = crop_image(image, size, position)

        # Simpan file hasil crop
        cropped_filename = f"cropped_{filename}"
        cropped_file_path = os.path.join(app.config['UPLOAD_FOLDER'], cropped_filename)
        cropped_image.save(cropped_file_path)

        return redirect(url_for('show_cropped', filename=cropped_filename))

    return render_template('crop.html', filename=filename, image_width=image.width, image_height=image.height)

@app.route('/cropped/<filename>')
def show_cropped(filename):
    cropped_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return render_template('cropped.html', filename=filename, cropped_file_path=cropped_file_path)


if __name__ == '__main__':
    app.run(debug=True, port=8000)
