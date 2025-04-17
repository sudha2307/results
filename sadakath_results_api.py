import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
import warnings

# Suppress InsecureRequestWarning for verify=False
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# Scraper function
def get_results(reg_no, exam):
    url = "https://results.sadakath.ac.in/resultpage.aspx"
    session = requests.Session()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }

    try:
        # First GET request to fetch the ViewState and other hidden fields
        response = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Safe fetch function for hidden input fields
        def safe_get(field_id):
            tag = soup.find('input', {'id': field_id})
            return tag['value'] if tag else None

        viewstate = safe_get('__VIEWSTATE')
        viewstategenerator = safe_get('__VIEWSTATEGENERATOR')
        eventvalidation = safe_get('__EVENTVALIDATION')

        # Check if all essential fields are found
        if not all([viewstate, viewstategenerator, eventvalidation]):
            print("❌ Error: Required hidden fields not found on the page.")
            return None

        # Now prepare the POST request payload
        payload = {
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            '__EVENTVALIDATION': eventvalidation,
            'TxtRegno': reg_no,
            'CMbExam': exam,
            'Button1': 'Submit'
        }

        # POST request to submit the form
        post_response = session.post(url, data=payload, headers=headers, verify=False)
        post_soup = BeautifulSoup(post_response.content, 'html.parser')

        # Parse results table
        results_table = post_soup.find('table', id='GridView1')
        if results_table:
            results = []
            rows = results_table.find_all('tr')[1:]  # Skip header row
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
            return results
        else:
            return None

    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return None


# Flask route for getting the result
@app.route('/get_result', methods=['POST'])
def get_result():
    data = request.get_json()  # Parse the JSON data from the request body
    reg_no = data.get('reg_no')  # Get the registration number
    exam = data.get('exam')  # Get the exam session

    if not reg_no or not exam:
        return jsonify({'error': 'Missing registration number or exam value'}), 400

    results = get_results(reg_no, exam)  # Call the get_results function with the provided data
    if results:
        return jsonify({'status': 'success', 'results': results})  # Return the results as JSON
    else:
        return jsonify({'status': 'error', 'message': 'No results found or invalid data.'}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
