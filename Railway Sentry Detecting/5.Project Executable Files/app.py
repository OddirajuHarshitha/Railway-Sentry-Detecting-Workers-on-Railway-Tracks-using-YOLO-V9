from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import os
from ultralytics import YOLO
from PIL import Image
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Define the path to the model
model_path = 'best.pt'

# Load the model
model = YOLO(model_path)


# model = YOLO('best.pt')

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'mp4', 'avi', 'mkv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect', methods=['GET', 'POST'])
def detect():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part'
        
        file = request.files['file']

        if file.filename == '':
            return "No selected file"
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                img = Image.open(filepath)
                model(img, save=True)
            
            elif filename.lower().endswith(('.mp4', '.avi', '.mkv')):
                model(filepath, save=True)

            return redirect(url_for('result', original_filename=filename))

    return render_template('detect.html')

@app.route('/result/<original_filename>')
def result(original_filename):
    folder_path ='runs/detect'
    subfolders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]    
    latest_subfolder = max(subfolders, key=lambda x: os.path.getctime(os.path.join(folder_path, x)))    
    directory = folder_path+'/'+latest_subfolder    
    print("printing directory:",directory) 
    files = os.listdir(directory)
    latest_file = files[0]
    
    print(latest_file)

    filename = os.path.join(folder_path, latest_subfolder, latest_file)

    file_extension = filename.rsplit('.', 1)[1].lower()

    environ = request.environ
    if file_extension == 'jpg':     
        return send_from_directory(directory,latest_file) #shows the result in seperate tab

    else:
        return "Invalid file format"
        
if __name__ == '__main__':
    app.run(debug=True)
