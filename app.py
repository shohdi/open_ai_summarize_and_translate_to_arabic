from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS
from PyPDF2 import PdfReader
import openai
from security.openapi_key import openai_key
import os
import shutil
from PIL import Image
import base64
import json
import io
import re
import time
import subprocess




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

def handleArabicTagsToSummary(text):
    pattern = r'<arabic>([^<]+)</arabic>'

    # Search for the pattern in the text
    match = re.search(pattern, text)

    if match:
        # Extract the content between the tags
        summary = match.group(1)
        print(summary)
    else:
        print("No content found between <arabic> and </arabic> tags.")
        summary = ' '
    
    return summary

def summarize_text(text):
    content = f"Please summarize the following technical text for normal non-technical person and show the output in arabic , The arabic summarized text should include all information found in the main text , show the arabic summarized text between <arabic> and </arabic>  , the text to summarize :\n\n{text}"

    response = callChatgpt(content)
    summary = response['choices'][0]['message']['content']
    summary = handleArabicTagsToSummary(summary)
    return summary
    

def image_to_base64_json(image):
    # Open the image file
    
    # Convert image to bytes
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    image_bytes = buffered.getvalue()
        
    # Encode image to base64
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
    # Create JSON object
    
    json_object = {
          "type": "image_url",
          "image_url": {
            "url": f"data:image/jpeg;base64,{image_base64}"
            ,"detail": "high"
          }
    }
        
    return json_object


def getImagesFromFile(file):
    ret=[]
    # Ensure the 'data' directory exists
    base_path = os.path.dirname(os.path.realpath(__file__))
    data_folder = os.path.join(base_path, 'data')
    os.makedirs(data_folder, exist_ok=True)
    fullFileName = os.path.join(data_folder,file.filename)
    file.save(fullFileName)
    pdf_file = fullFileName
    pathDir = data_folder
    pathName = file.filename + "_ext"
    extFullPath = pathDir + os.path.sep + pathName
    
    
    print(extFullPath)
 
    if(os.path.exists(extFullPath)):
        shutil.rmtree(extFullPath)
    
    if(not os.path.exists(extFullPath)):
        os.mkdir(extFullPath)
    
        
    print('start converting pdf to images in ',extFullPath + os.path.sep)
    command = []
    command.append('pdftoppm')
    command.append(pdf_file)
    command.append( extFullPath + os.path.sep )
    result = subprocess.run(command, capture_output=True, text=True)
    output = ''
    if result.returncode == 0:
        output = result.stdout
    else:
        output = result.stderr
        

    #cmdLine = 'pdftoppm '
    #cmdLine = cmdLine + '-l ' + str(lastPage) + ' '
    #cmdLine = cmdLine  +'"' +pdf_file+'"' + ' '
    #cmdLine = cmdLine  + '"' + extFullPath + os.path.sep + '"'


    #stream = os.popen(cmdLine)
    #output = stream.read()
    
    if "error" in output.lower():
        raise Exception(output)
    
    imageNames =  os.listdir(extFullPath)
    imageNames.sort()
    
    indx = 1
    for image in imageNames:
        print(image)
        if ('ppm' in image):
            #found image
            # Open the .ppm image
            imageName = os.path.join(extFullPath,image)
            newJpgPath = os.path.join(extFullPath,'jpg')
            os.makedirs(newJpgPath, exist_ok=True)
            newImageName = os.path.join(newJpgPath,image + '.jpg')
            print(imageName)
            print(newImageName)
           
            input_image = Image.open(imageName)
            # Resize the image to 1024x768
            resized_image = None
            width = 1024
            height = 768
            origWidth = input_image.size[0]
            origHeight = input_image.size[1]
            
            if origWidth > origHeight:
                width = 1024
                height = int(width * origHeight/origWidth)
            else:
                height = 1024
                width = int(height * origWidth/origHeight)
            
                
            resized_image = input_image.resize((width, height))
            # Save the image as .jpg
            resized_image.save(newImageName, format="JPEG")
            jsonImage = image_to_base64_json(resized_image)
            ret.append(jsonImage)
            
    return ret
    
def callChatgpt(content):
    error = 'Rate limit'
    response = None
    while error is not None:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",  # or use "gpt-3.5-turbo"
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": content}
                ],
                max_tokens=10000  # You can adjust the max tokens as needed
            )
            return response
        except Exception as e:
            # Convert the exception to a string
            error = str(e)
            if 'Rate limit' in error:
                time.sleep(65)
    
    return response

        
    


        


def summarize_text_by_image(file):
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

class SummarizePDFByImage(Resource):
    def post(self):
        if 'file' not in request.files:
            return {"error": "No file part"}, 400
        file = request.files['file']
        if file.filename == '':
            return {"error": "No selected file"}, 400
        if file and file.filename.endswith('.pdf'):
            
            summary = summarize_text_by_image(file)
            return {"summary": summary}, 200
        else:
            return {"error": "Invalid file format. Please upload a PDF file."}, 400

api.add_resource(SummarizePDF, '/summarize')
api.add_resource(SummarizePDFByImage, '/sumimage')

if __name__ == '__main__':
    app.run(debug=True,port=5001)