from flask import Flask, request, jsonify, render_template
import os, base64
from processor import image_to_braille_text

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs('uploads', exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/decode', methods=['POST'])
def decode():
    image_bytes = None
    if 'file' in request.files:
        f = request.files['file']
        if f.filename == '':
            return jsonify({"error": "No file selected"}), 400
        image_bytes = f.read()
    elif request.is_json:
        data = request.get_json()
        if 'image' in data:
            img_data = data['image']
            if ',' in img_data:
                img_data = img_data.split(',')[1]
            image_bytes = base64.b64decode(img_data)
    if image_bytes is None:
        return jsonify({"error": "No image provided"}), 400
    result = image_to_braille_text(image_bytes)
    return jsonify(result)

@app.route('/api/tts', methods=['POST'])
def tts():
    try:
        from gtts import gTTS
        import io
        data = request.get_json()
        text = data.get('text', '').strip()
        if not text or text == '(unrecognized pattern)':
            return jsonify({"error": "No text to speak"}), 400
        tts_obj = gTTS(text=text, lang='en', slow=False)
        audio_buffer = io.BytesIO()
        tts_obj.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        audio_b64 = base64.b64encode(audio_buffer.read()).decode('utf-8')
        return jsonify({"audio": audio_b64})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)