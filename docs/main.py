# main.py
from flask import Flask, request, jsonify
from cen_tari_translator import translate_cen_tari
from cen_tari_runtime import execute_python_code

app = Flask(__name__)

@app.route('/run', methods=['POST'])
def run_code():
    data = request.get_json()
    cen_tari_code = data.get('code', '')
    try:
        python_code = translate_cen_tari(cen_tari_code)
        output = execute_python_code(python_code)
        return jsonify({'output': output})
    except Exception as e:
        return jsonify({'output': f'Error: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True)
