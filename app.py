from flask import Flask, request, render_template
import pickle
import numpy as np
import smtplib
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)

try:
    model = pickle.load(open('model.pkl', 'rb'))
except Exception as e:
    print(f"Error loading model: {e}")

def send_email(message):
    try:
        # Email configuration
        sender_email = "sajjadsaleem341@gmail.com"
        receiver_email = "sajjadsaleem442@gmail.com"
        password = "fxieweuzdhrbsekm"

        # Create the HTML content for the email
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #fff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #333; text-align: center;">⚠️ Forest Fire Alert</h2>
                <p style="font-size: 16px; color: #555;">Dear Forest Management,</p>
                <p style="font-size: 16px; color: #555;">
                    This is to notify you that there is a high probability of a forest fire occurring in your area.
                </p>
                <p style="font-size: 16px; color: #333; font-weight: bold;">Probability of fire: {message}</p>

                <p style="font-size: 14px; color: #777; margin-top: 40px; text-align: center;">
                    Stay safe, <br>
                    Forest Fire Monitoring Team
                </p>
            </div>
        </body>
        </html>
        """
        
        # Create the email message object
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "Forest Fire Alert 🚨"
        msg['From'] = sender_email
        msg['To'] = receiver_email

        # Attach the HTML content to the email
        msg.attach(MIMEText(html_content, 'html'))

        # Send the email using Gmail's SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
            print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

@app.route('/')
def hello_world():
    return render_template("index.html")

import threading

def send_email_async(message):
    threading.Thread(target=send_email, args=(message,)).start()

@app.route('/predict', methods=['POST', 'GET'])
def predict():
    try:
        # Extract features from the form
        int_features = [float(x) for x in request.form.values()]
        final_features = [np.array(int_features)] 
        print("Features from form:", int_features)
        print("Final input to model:", final_features)
        
        # Predict fire occurrence probability
        prediction = model.predict_proba(final_features)
        output = prediction[0][1]  # Probability of fire occurring
        
        formatted_output = '{0:.2f}'.format(output)  # Format output to 2 decimal places

        # Check if probability is greater than 0.5
        if output > 0.5:
            # Send an email asynchronously
            send_email_async(formatted_output)
            
            # Render template with warning message
            return render_template('index.html', 
                                   msg1='Your Forest is in Danger.', 
                                   pred=formatted_output)
        else:
            # Render template with safe message
            return render_template('index.html', 
                                   msg1='Your Forest is Safe.', 
                                   pred=formatted_output)
    except Exception as e:
        # Handle errors and display error message
        return render_template('index.html', 
                               res='Error occurred during prediction.',
                               res2= 'Please check input values.', 
                               msg=str(e))
    
if __name__ == '__main__':
    app.run(debug=True)
