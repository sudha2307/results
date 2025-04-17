from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)  # to handle Flutter cross-origin requests

# Scraper function
def get_results(reg_no, exam):
    url = "https://results.sadakath.ac.in/ResultPage.aspx"
    payload = {
        '__VIEWSTATE': '/wEPDwUJNzE3NDI4OTM5D2QWAgIBD2QWAgIDDxBkDxYBZhYBEAUITm92IDIwMjQFCE5vdiAyMDI0Z2RkZIR/zXQeTg+jyVZbtMreusymyMQ4',
        '__VIEWSTATEGENERATOR': '7C3C6012',
        '__EVENTVALIDATION': '/wEdAARzN7bZtmqtQXfSWIF0CIprZS6BASrBkr5QeAzZHQV1+txSYZLFsAialTI1fBLjIvnN+DvxnwFeFeJ9MIBWR693ivjs57FeIsSCjQoYF9sSNQrUVAY=',
        'TxtRegno': reg_no,
        'CMbExam': exam,
        'Button1': 'Submit'
    }

    print(f"🔍 Fetching result for: {reg_no}, {exam}")
    response = requests.post(url, data=payload, verify=False)
    print(f"📥 Response received (status code: {response.status_code})")

    soup = BeautifulSoup(response.content, 'html.parser')

    # Parsing the result page
    results_table = soup.find('table', id='GridView1')
    if results_table:
        print("✅ Results table found.")
        results = []
        rows = results_table.find_all('tr')[1:]  # Skip header
        for row in rows:
            columns = row.find_all('td')
            result = {
                'sub_code': columns[0].text.strip(),
                'sub_name': columns[1].text.strip(),
                'int_mark': columns[2].text.strip(),
                'ext_mark': columns[3].text.strip(),
                'total': columns[4].text.strip(),
                'result': columns[5].text.strip()
            }
            results.append(result)
        print(f"🎉 Total subjects found: {len(results)}")
        return results
    else:
        print("❌ No results table found.")
        return None


# Flask API route
@app.route('/get_result', methods=['POST'])
def get_result():
    data = request.get_json()
    reg_no = data.get('reg_no')
    exam = data.get('exam')

    print(f"📥 API call received: reg_no={reg_no}, exam={exam}")

    if not reg_no or not exam:
        return jsonify({'error': 'Missing registration number or exam value'}), 400

    results = get_results(reg_no, exam)
    if results:
        return jsonify({'status': 'success', 'results': results})
    else:
        return jsonify({'status': 'error', 'message': 'No results found or invalid data.'}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
