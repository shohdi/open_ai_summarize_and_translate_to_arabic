from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from PyPDF2 import PdfReader
import openai
from security.openapi_key import openai_key

# Set your OpenAI API key
openai.api_key = openai_key['key']

app = Flask(__name__)
CORS(app)  # Enable CORS
api = Api(app)

def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text

def summarize_text(text):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # or use "gpt-3.5-turbo"
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Please summarize the following technical text for normal non-technical person and show the output in arabic , the text to summarize :\n\n{text}"}
        ],
        max_tokens=10000  # You can adjust the max tokens as needed
    )
    summary = response['choices'][0]['message']['content']
    return summary

class SummarizePDF(Resource):
    def post(self):
        if 'file' not in request.files:
            return {"error": "No file part"}, 400
        file = request.files['file']
        if file.filename == '':
            return {"error": "No selected file"}, 400
        if file and file.filename.endswith('.pdf'):
            text = extract_text_from_pdf(file)
            summary = summarize_text(text)
            return {"summary": summary}, 200
        else:
            return {"error": "Invalid file format. Please upload a PDF file."}, 400

api.add_resource(SummarizePDF, '/summarize')

if __name__ == '__main__':
    app.run(debug=True,port=5001)