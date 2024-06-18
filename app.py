from flask import Flask, request, render_template
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

endpoint = os.getenv("FORM_RECOGNIZER_ENDPOINT")
key = os.getenv("FORM_RECOGNIZER_KEY")

document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        file_content = file.read()
        poller = document_analysis_client.begin_analyze_document(
            "prebuilt-tax.us.w2", document=file_content)
        w2s = poller.result()

        results = []
        for idx, w2 in enumerate(w2s.documents):
            result = {"index": idx + 1, "fields": {}}
            for name, field in w2.fields.items():
                if isinstance(field.value, list):
                    field_info = []
                    for item in field.value:
                        if isinstance(item.value, dict):
                            item_info = {item_field_name: item_field.value for item_field_name, item_field in item.value.items()}
                        else:
                            item_info = str(item.value)
                        field_info.append(item_info)
                elif isinstance(field.value, dict):
                    field_info = {item_field_name: item_field.value for item_field_name, item_field in field.value.items()}
                else:
                    field_info = str(field.value)
                result["fields"][name] = {"value": field_info, "confidence": field.confidence}
            results.append(result)
        return render_template('results.html', results=results)
    return "No file uploaded", 400

if __name__ == '__main__':
    app.run(debug=True)
