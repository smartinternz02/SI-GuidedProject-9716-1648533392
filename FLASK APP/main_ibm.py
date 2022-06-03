from unicodedata import category
from flask import Flask, render_template, request, flash
import pickle

import requests

# NOTE: you must manually set API_KEY below using information retrieved from your IBM Cloud account.
API_KEY = "wbHWaymahrb_xaVy5cBfi7qV2WlI5mMYrQBr7lR-I_nY"
token_response = requests.post('https://iam.cloud.ibm.com/identity/token', data={"apikey":
 API_KEY, "grant_type": 'urn:ibm:params:oauth:grant-type:apikey'})
mltoken = token_response.json()["access_token"]

header = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + mltoken}


app = Flask(__name__)
#model = pickle.load(open('model.pkl', 'rb'))
sc = pickle.load(open('transform.pkl', 'rb'))

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/predict", methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        cc = float(request.form.get('cloudCover'))
        ar = float(request.form.get('aRain'))
        jfr = float(request.form.get('jfRain'))
        mmr = float(request.form.get('mmRain'))
        jsr = float(request.form.get('jsRain'))
        arr = [[cc, ar, jfr, mmr, jsr]]
        arr = sc.transform(arr).tolist()
        #val = model.predict(sc.transform(arr))

        payload_scoring = {"input_data": [{ "fields" : [["f0","f1","f2","f3","f4"]], "values" : arr }]}

        response_scoring = requests.post('https://us-south.ml.cloud.ibm.com/ml/v4/deployments/a09d8c33-f2a2-4eca-ab8b-0e6d5ae5217f/predictions?version=2022-06-01', json=payload_scoring,
        headers={'Authorization': 'Bearer ' + mltoken})
        print("Scoring response")
        #print(response_scoring.json())
        pred = response_scoring.json()
        output = pred["predictions"][0]['values'][0][0]
        #print(output)
        val = output

        if(round(val)==1):
            final = "Possibility of severe flood"
        else:
            final = "No possibility of severe flood"
    else:
        final = ""
    return render_template("predict.html", y=final)

if __name__ == '__main__':
    app.run(debug=False)
    app.secret_key = 'qwerty123'