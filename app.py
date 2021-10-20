# import the Flask class from the flask module
import flask
from flask import Flask, render_template, redirect, url_for, request
from sample import feature_extraction_from_database

# create the application object
app = Flask(__name__)

@app.route('/predict', methods = ['POST'])
def predict():


    sample_id = int(request.form['sample_id'])
    result,final_prediction = feature_extraction_from_database(sample_id)
    return render_template('index.html', tables=[result.to_html(classes='data',index = False)],final_prediction=final_prediction)

    #except:
    #  sample_id = int(request.form['sample_id'])

    #  return render_template('index.html', prediction_text= '{} is Not a valid sample id as it cannot be Fetched from Database. Please get in touch with the team'.format(sample_id))






# route for handling the login page logic
@app.route('/',methods = ['GET','POST'])
def login():
    error = None
    a = {'owais.ahmed@canarydetect.com': 'Canary@2021', 'r.varsha@canarydetect.com': 'Canary@2021'}

    if request.method == 'POST':
        if request.form['username'] in a and a[request.form['username']] == request.form['password']:
            return render_template('index.html')

        else:
            error = 'Invalid Credentials. Please try again.'

    return render_template('login.html', error=error)



# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)
