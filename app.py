from flask import Flask, request, Response, render_template
from generate_images import generate_images
from PIL import Image
import io

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_images', methods=['POST'])
def generate_images_route():
    input_string = request.form['input_string'] 
    images = generate_images(input_string)
    response = Response(images, mimetype='multipart/x-mixed-replace; boundary=frame')
    return response
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)