from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS
from PyPDF2 import PdfReader


from lib import handleArabicTagsToSummary
from lib import callChatgpt

class SummarizePDF(Resource):
    def post(self):
        if 'file' not in request.files:
            return {"error": "No file part"}, 400
        file = request.files['file']
        if file.filename == '':
            return {"error": "No selected file"}, 400
        if file and file.filename.endswith('.pdf'):
            text = self.extract_text_from_pdf(file)
            summary = self.summarize_text(text)
            return {"summary": summary}, 200
        else:
            return {"error": "Invalid file format. Please upload a PDF file."}, 400
    def extract_text_from_pdf(self,file):
        reader = PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text


    def summarize_text(self,text):
        content = f"Please summarize the following technical text for normal non-technical person and show the output in arabic , The arabic summarized text should include all information found in the main text , show the arabic summarized text between <arabic> and </arabic>  , the text to summarize :\n\n{text}"

        response = callChatgpt(content)
        summary = response['choices'][0]['message']['content']
        summary = handleArabicTagsToSummary(summary)
        return summary