from flask import Flask, jsonify, request
from pythainlp import word_tokenize
from pythainlp.util import rank
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app, resources={r"/lexto": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
def hello():
    return "Welcome"


@app.route('/lexto', methods=['GET'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def get_api():
    text = request.args.get('text')
    proc = word_tokenize(text)
    print(proc)
    return jsonify(proc)

if __name__ == "__main__":
    app.run(debug=False)