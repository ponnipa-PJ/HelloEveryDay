from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import pickle
import pandas as pd

app = Flask(__name__)
cors = CORS(app, resources={r"/lexto": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
def hello():
    return "Welcome To WebService"

@app.route('/predictmotor')
def get_predictmotor():
    print(request.args.get)
    temp_in = request.args.get('temp_out')
    if temp_in is None:
        return jsonify(str('temp out not incorrect'))
    else:
        loaded_model = pickle.load(open('baggingmodel.sav', 'rb'))
        data = {"Temp_Out_Y": [temp_in]}
        # print(data)
        # #load data into a DataFrame object:
        df = pd.DataFrame(data)
        # print(df)
        X = loaded_model.predict(df)
        pre = X[0]
        # print(pre)
        return jsonify(str(pre))

if __name__ == "__main__":
    app.run(debug=False)