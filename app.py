from flask import Flask, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename
import asyncio
from automation import process_rows_async
import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return filename.endswith('.json')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_automation():
    if 'json_file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['json_file']
    sheet_name = request.form.get('sheet_name')
    
    if not sheet_name:
        return jsonify({'error': 'Sheet name is required'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Setup Google Sheets
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            creds = ServiceAccountCredentials.from_json_keyfile_name(filepath, scope)
            client = gspread.authorize(creds)
            sheet = client.open(sheet_name).sheet1
            
            all_values = sheet.get_all_values()
            num_rows = len(all_values)
            
            # Run automation in background
            asyncio.run(process_rows_async(all_values, 1, sheet))
            
            return jsonify({'message': 'Automation started successfully'})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            # Clean up the uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/stop', methods=['POST'])
def stop_automation():
    # Implementation for stopping the automation
    # This would need to be implemented with proper process management
    return jsonify({'message': 'Automation stopped'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))