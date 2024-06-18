# Import the necessary modules
from flask import Flask, render_template, request
import os
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# Create an instance of the Flask application
app = Flask(__name__)

# Retrieve the endpoint and key from environment variables
endpoint = os.getenv('FORM_RECOGNIZER_ENDPOINT')
key = os.getenv('FORM_RECOGNIZER_KEY')

# Create a DocumentAnalysisClient instance using the endpoint and key
document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))

# Define a route for the root URL
@app.route('/')
def index():
    return render_template('index.html')

# Define a route for the '/upload' URL with POST method
@app.route('/upload', methods=['POST'])
def upload():
    # Retrieve the formUrl from the request form data
    formUrl = request.form['formUrl']
    
    # Analyze the document from the provided formUrl using the DocumentAnalysisClient
    poller = document_analysis_client.begin_analyze_document_from_url("prebuilt-tax.us.w2", formUrl)
    w2s = poller.result()

    # Process the analyzed results
    results = []
    for idx, w2 in enumerate(w2s.documents):
        result = {"index": idx + 1, "fields": {}}
        for name, field in w2.fields.items():
            field_info = {"value": field.value, "confidence": field.confidence}
            if name in ["AdditionalInfo", "Employee", "Employer", "LocalTaxInfos", "StateTaxInfos"]:
                field_info["value"] = []
                for item in field.value:
                    item_info = {item_field_name: item_field.value for item_field_name, item_field in item.value.items()}
                    field_info["value"].append(item_info)
            result["fields"][name] = field_info
        results.append(result)
    
    # Render the 'results.html' template with the processed results
    return render_template('results.html', results=results)

# Run the Flask application if this script is executed directly
if __name__ == '__main__':
    app.run(debug=True)