from flask import Flask
from flask_restful import  Api
from flask_cors import CORS
import openai
from security.openapi_key import openai_key
from summarize_pdf_by_image import SummarizePDFByImage
from summarize_pdf import SummarizePDF
from conclusion_pdf_by_image import ConclusionPDFByImage


# Set your OpenAI API key
openai.api_key = openai_key['key']

app = Flask(__name__)
CORS(app)  # Enable CORS
api = Api(app)


api.add_resource(SummarizePDF, '/summarize')
api.add_resource(SummarizePDFByImage, '/sumimage')
api.add_resource(ConclusionPDFByImage,'/conimage')

if __name__ == '__main__':
    app.run(debug=True,port=5001)