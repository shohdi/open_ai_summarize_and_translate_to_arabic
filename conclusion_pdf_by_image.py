from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from lib import getImagesFromFile,callChatgpt,handleArabicTagsToSummary

class ConclusionPDFByImage(Resource):
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
        summary = ''
        ind = 0
        for img in imagePathsFull:
            ind = ind + 1
            imagePaths = [img]
            content=[{"type":"text"
                    ,"text":f"Please analyze these images and provide a summary of all information found in them"}]
            content.extend(imagePaths)
        
        
            response = callChatgpt(content)
            summary = response['choices'][0]['message']['content']
            fullSummary = fullSummary + ' ' + f'\nPage No : {ind}\n' + ' ' + summary

        summary = fullSummary 

        
        content =f"write a summary of the following text , if the text have conclusion part then summary should include this conclusion , text : {summary}"
        response = callChatgpt(content)
        summary = response['choices'][0]['message']['content']

        content =f"Translate this text to arabic : {summary}"
        response = callChatgpt(content)
        summary = response['choices'][0]['message']['content']

        
            
        
        return summary
    
    
