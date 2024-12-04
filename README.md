<h1>Calorie-Prediction-Model(Machine Learning)</h1>
This project is a Python-based application that predicts the number of calories burned during physical activities. It uses machine learning techniques to make predictions and features a Flask-based web interface with a MySQL database for user authentication.

<h2>Features</h2>
Predict calorie burn based on user inputs such as age, weight, height, and activity duration.
User authentication with MySQL database integration.
Secure and interactive interface for input handling and displaying results.
<br>
<h2>Technologies Used</h2>
Programming Language: Python
<br>
Libraries: Pandas, NumPy, scikit-learn, Matplotlib, Flask
<br>
Database: MySQL
<br>
IDE: PyCharm
<br>
<h3>Project Structure</h3>
<br>

|-- app.py                  # Main application file  
|-- rfr.pkl                 # Trained Random Forest model  
|-- templates/              # HTML templates  
    |-- index.html          # Login page  
    |-- about.html          # About page  
    |-- prediction.html     # Prediction page  
|-- static/                 # Static files (CSS, JS, images)  
|-- requirements.txt        # Python dependencies 
<br>
<h2>Setup Instructions</h2>
<br>
<h3>Clone the Repository</h3>

bash
Copy code
git clone https://github.com/yourusername/calorie-burn-prediction.git  
cd calorie-burn-prediction  
Install Dependencies
Ensure you have Python 3.x installed. Then run:

bash
Copy code
pip install -r requirements.txt  
Set Up the Database

Create a MySQL database and table for user authentication.
Update the database credentials in app.py.
Run the Application
Open PyCharm and run the app.py file. The application will be available at:

arduino
Copy code
http://127.0.0.1:5000  
Test the Application

Log in using the credentials stored in the database.
Enter the required inputs to get calorie burn predictions.
Dataset
The dataset used for training the model includes user attributes such as age, weight, height, activity duration, and calories burned.

Model
The predictive model is built using a Random Forest Regressor, achieving an accuracy of 85% during testing.

Future Enhancements
Add more user-friendly features to the interface.
Improve model accuracy with additional features and fine-tuning.
Deploy the application on a cloud platform for wider access.
