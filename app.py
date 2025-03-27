from flask import Flask, request, render_template
import boto3
import os


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    endpoint_name=None
    try:
        # Get data from form
        area = request.form['area']
        perimeter = request.form['perimeter']
        major_axis_length = request.form['major_axis_length']
        minor_axis_length = request.form['minor_axis_length']
        eccentricity = request.form['eccentricity']
        convex_area = request.form['convex_area']
        extent = request.form['extent']

        # Create a comma-separated string of the input values
        payload = f"{area},{perimeter},{major_axis_length},{minor_axis_length},{eccentricity},{convex_area},{extent}"
        with open('current_endpoint_name.txt','rb') as fp:
            endpoint_name=fp.read()
            endpoint_name=endpoint_name.decode('utf-8')

        sgmkr_runt = boto3.client('sagemaker-runtime', region_name='us-east-1')
        response = sgmkr_runt.invoke_endpoint(
        EndpointName=endpoint_name, ContentType="text/csv", Body=payload,
        )
        prediction = response["Body"].read().decode()
        
        return render_template('index.html', prediction_text='Predicted Value of the rice ML-project : {}'.format(prediction))
    except Exception as e:
        return render_template('index.html', prediction_text='Error: {}'.format(str(e)))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    #app.run(debug=True)
