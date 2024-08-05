from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from lib import getImagesFromFile,callChatgpt,handleArabicTagsToSummary

class SummarizePDFByImage(Resource):
    def post(self):
        if 'file' not in request.files:
            return {"error": "No file part"}, 400
        file = request.files['file']
        if file.filename == '':
            return {"error": "No selected file"}, 400
        if file and file.filename.endswith('.pdf'):
            
            summary = self.summarize_text_by_image(file)
            return {"summary": summary}, 200
        else:
            return {"error": "Invalid file format. Please upload a PDF file."}, 400

    def summarize_text_by_image(self,file):
        imagePathsFull= getImagesFromFile(file)
        fullSummary = ''
        for img in imagePathsFull:
            imagePaths = [img]
            content=[{"type":"text"
                    ,"text":f"Please summarize the following technical text for normal non-technical person and show the output in arabic , The arabic summarized text should include all information found in the main text , show the arabic summarized text between <arabic> and </arabic> , the text to summarize is in the images provided"}]
            content.extend(imagePaths)
            
            
            response = callChatgpt(content)
            summary = response['choices'][0]['message']['content']
            summary = handleArabicTagsToSummary(summary)
            fullSummary = fullSummary + ' ' + summary
            
        summary = fullSummary
        return summary
    
    
