from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Server is alive! Use POST /predict with JSON {\"feature\": [1,2,3]}"

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    input_feature = data.get('feature', [])
    
    prediction = sum(input_feature) * 2
    
    return jsonify({
        'status': 'success',
        'input': input_feature,
        'prediction': prediction
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
