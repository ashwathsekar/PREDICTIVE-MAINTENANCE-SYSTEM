from flask import Flask, request, render_template_string
import joblib
import pandas as pd
import os 

app = Flask(__name__)

# Load the trained model
#model_path = "D:/AAA Semester 6/Innovation Practise Lab Project/machine_failure_model_updated.pkl"
model_path = os.path.join(os.getcwd(), "models", "machine_failure_model_updated.pkl")
modele = joblib.load(model_path)

# HTML Form for User Input
html_form = '''
<!DOCTYPE html>
<html>
<head>
    <title>Predictive Maintenance</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .container { padding-top: 50px; max-width: 600px; }
    </style>
</head>
<body>
    <div class="container">
        <h2 class="mb-4 text-center">Enter Data for Prediction</h2>
        <form action="/predict" method="post">
            <div class="mb-3"><label class="form-label">Air temperature [K]:</label>
            <input type="number" class="form-control" name="Air temperature [K]" step="any" required></div>
            
            <div class="mb-3"><label class="form-label">Process temperature [K]:</label>
            <input type="number" class="form-control" name="Process temperature [K]" step="any" required></div>
            
            <div class="mb-3"><label class="form-label">Rotational speed [rpm]:</label>
            <input type="number" class="form-control" name="Rotational speed [rpm]" step="any" required></div>
            
            <div class="mb-3"><label class="form-label">Torque [Nm]:</label>
            <input type="number" class="form-control" name="Torque [Nm]" step="any" required></div>
            
            <div class="mb-3"><label class="form-label">Tool wear [min]:</label>
            <input type="number" class="form-control" name="Tool wear [min]" step="any" required></div>
            
            <div class="mb-3"><label class="form-label">Type_H:</label>
            <input type="number" class="form-control" name="Type_H" step="any" required></div>
            
            <div class="mb-3"><label class="form-label">Type_L:</label>
            <input type="number" class="form-control" name="Type_L" step="any" required></div>
            
            <div class="mb-3"><label class="form-label">Type_M:</label>
            <input type="number" class="form-control" name="Type_M" step="any" required></div>
            
            <button type="submit" class="btn btn-primary w-100">Predict</button>
        </form>
    </div>
</body>
</html>
'''

# Result Page Template
result_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Prediction Result</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        .container { padding-top: 50px; text-align: center; max-width: 600px; }
        .result-box { padding: 30px; border-radius: 10px; font-size: 22px; font-weight: bold; }
        .failure { background-color: #ff4d4d; color: white; }
        .no-failure { background-color: #28a745; color: white; }
        .suggestions { margin-top: 20px; padding: 20px; background-color: #f8f9fa; border-radius: 10px; text-align: left; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Prediction Result</h2>
        <div class="result-box {{ css_class }}">{{ prediction_text }}</div>
        
        {% if failure_types %}
        <div class="suggestions">
            <h4> Failure Type(s) Detected:</h4>
            <ul>
                {% for failure in failure_types %}
                <li><strong>{{ failure }}</strong></li>
            </ul>
            <h5> Tips to Prevent {{ failure }}:</h5>
            <ol>
                {% if failure == "Tool Wear Failure" %}
                    <li>  Regularly replace worn-out tools.</li>
                    <li>  Maintain proper lubrication to reduce wear.</li>
                    <li>  Use high-quality cutting materials for durability.</li>
                {% elif failure == "Heat Dissipation Failure" %}
                    <li>  Ensure proper cooling system operation.</li>
                    <li>  Maintain air temperature to avoid overheating.</li>
                    <li>  Regularly check heat sinks & ventilation.</li>
                {% elif failure == "Power Failure" %}
                    <li> Use stable power sources with surge protectors.</li>
                    <li> Regularly inspect power cables & connections.</li>
                    <li> Implement backup power solutions if needed.</li>
                {% elif failure == "Overstrain Failure" %}
                    <li> Reduce excessive load on machinery.</li>
                    <li> Implement gradual stress-testing on materials.</li>
                    <li> Regularly inspect machine components for stress fractures.</li>
                {% elif failure == "Random Failure" %}
                    <li> Conduct routine maintenance checks.</li>
                    <li> Analyze historical failure patterns for insights.</li>
                    <li> Improve system redundancy for better reliability.</li>
                {% elif failure == "Unknown Failure" %}
                    <li> Run detailed diagnostics to identify unknown issues.</li>
                    <li> Review machine logs for anomalies.</li>
                    <li> Consult maintenance experts for further investigation.</li>
                {% endif %}
            </ol>
            {% endfor %}
        </div>
        {% endif %}
        
        <a href="/" class="btn btn-primary mt-4">Try Again</a>
    </div>
</body>
</html>

'''


@app.route('/', methods=['GET'])
def home():
    return render_template_string(html_form)


@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Convert form data to float
        data = {key: float(value) for key, value in request.form.items()}
        data_df = pd.DataFrame([data])

        # Define expected feature order
        expected_columns = [
            "Air temperature [K]", "Process temperature [K]", "Rotational speed [rpm]",
            "Torque [Nm]", "Tool wear [min]", "Type_H", "Type_L", "Type_M"
        ]
        data_df = data_df[expected_columns]

        # Make predictions
        predictions = modele.predict(data_df)
        machine_failure = predictions[0][0]  # Machine failure (0 or 1)
        
        # Map failure types to full names
        failure_mapping = {
            "TWF": "Tool Wear Failure",
            "HDF": "Heat Dissipation Failure",
            "PWF": "Power Failure",
            "OSF": "Overstrain Failure",
            "RNF": "Random Failure"
        }
        failure_types = ["TWF", "HDF", "PWF", "OSF", "RNF"]
        detected_failures = [failure_mapping[failure_types[i]] for i in range(5) if predictions[0][i+1] == 1]

        # Handle unknown failure case
        if machine_failure == 1 and not detected_failures:
            detected_failures.append("Unknown Failure")

        # Define result message
        prediction_text = "✅ No Failure" if machine_failure == 0 else "⚠️ Machine Failure Detected!"
        css_class = "no-failure" if machine_failure == 0 else "failure"

        return render_template_string(result_template, prediction_text=prediction_text, css_class=css_class, failure_types=detected_failures)

    except Exception as e:
        return f"Error: {str(e)}"


#if __name__ == '__main__':
#   app.run(debug=True)



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))  # Use Render's PORT or default 10000
    app.run(host='0.0.0.0', port=port)      #Allows external access to your Flask app.
