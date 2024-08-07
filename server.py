from flask import Flask, request, jsonify
from flask_cors import CORS
from googletrans import Translator
import speech_recognition as sr
from pydub import AudioSegment
import os

app = Flask(__name__)
CORS(app)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        # Save the uploaded file temporarily
        temp_filename = 'temp.mp3'
        file.save(temp_filename)

        # Convert MP3 to WAV
        sound = AudioSegment.from_mp3(temp_filename)
        wav_filename = 'temp.wav'
        sound.export(wav_filename, format="wav")

        # Perform speech recognition
        r = sr.Recognizer()
        with sr.AudioFile(wav_filename) as source:
            audio = r.record(source)
        
        try:
            # Assuming the audio is in Arabic
            text = r.recognize_google(audio, language="ar-AR")
            
            # Clean up temporary files
            os.remove(temp_filename)
            os.remove(wav_filename)
            
            return jsonify({'transcription': text})
        except sr.UnknownValueError:
            return jsonify({'error': 'Speech recognition could not understand the audio'}), 400
        except sr.RequestError as e:
            return jsonify({'error': f'Could not request results from speech recognition service; {e}'}), 500

@app.route('/translate', methods=['POST'])
def translate():
    data = request.json
    arabic_text = data.get('text', '')
    
    if not arabic_text:
        return jsonify({'error': 'No text provided'}), 400

    translator = Translator()
    try:
        translation = translator.translate(arabic_text, src='ar', dest='en')
        return jsonify({'translation': translation.text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)