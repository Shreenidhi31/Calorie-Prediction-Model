from flask import Flask, request, render_template, redirect, url_for, flash
import mysql.connector
import pandas as pd
import numpy as np
import pickle
from werkzeug.security import generate_password_hash, check_password_hash  # For password hashing
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for using flash messages

# MySQL connection setup
def get_db_connection():
    connection = mysql.connector.connect(
        host='Your hostname',
        user='Your DB user name',  # Replace with your MySQL username
        password='Your DB Password',  # Replace with your MySQL password
        database='Your DB name'  # Replace with your database name
    )
    return connection


# Load the trained model
rfr = pickle.load(open('rfr.pkl', 'rb'))


# Prediction function
def pred(Gender, Age, Height, Weight, Duration, Heart_rate, Body_temp):
    if Gender.lower() == 'male':
        Gender = 1
    elif Gender.lower() == 'female':
        Gender = 0
    else:
        raise ValueError("Invalid gender value. Please use 'male' or 'female'.")
    features = np.array([[Gender, Age, Height, Weight, Duration, Heart_rate, Body_temp]])
    prediction = rfr.predict(features).reshape(1, -1)
    return prediction[0][0]


def calculate_bmi(height, weight, gender):
    height_in_meters = height / 100.0  # convert height from cm to meters
    bmi = weight / (height_in_meters ** 2)

    # Determine the BMI category
    if bmi < 18.5:
        category = 'Underweight'
    elif 18.5 <= bmi < 24.9:
        category = 'Normal weight'
    elif 25 <= bmi < 29.9:
        category = 'Overweight'
    else:
        category = 'Obese'

    return round(bmi, 2), category  # Return both BMI and category


# Generate BMI chart
def generate_bmi_chart(bmi):
    categories = ['Underweight', 'Normal weight', 'Overweight', 'Obesity']
    category_colors = ['lightblue', 'green', 'orange', 'red']
    bmi_ranges = [(0, 18.5), (18.5, 24.9), (24.9, 29.9), (29.9, 40)]

    # Create the vertical bar chart
    fig, ax = plt.subplots(figsize=(10, 5))

    # Plot vertical bars with different colors for each category
    for idx, (low, high) in enumerate(bmi_ranges):
        ax.bar(categories[idx], high, color=category_colors[idx], edgecolor='black')
        ax.text(idx, high / 2, f'{low} - {high}', ha='center', va='center')

    # Plot user's BMI as a horizontal line on the chart
    ax.axhline(bmi, color='blue', linestyle='--', label=f'Your BMI: {bmi}')
    ax.set_ylim(0, 40)  # Adjust the y-axis limit to match the highest BMI range
    plt.ylabel('BMI')
    plt.title('BMI Categories and Your Result')
    plt.legend()

    # Save the plot to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    return chart_data


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')

# Admin dashboard route
@app.route('/admin_dashboard')
def admin_dashboard():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Get the total number of users
        cursor.execute("SELECT COUNT(*) AS total_users FROM users")
        total_users = cursor.fetchone()['total_users']

        # Fetch all user details from the 'users' table
        cursor.execute("SELECT id,name,email FROM users")  # Using 'id' from your table
        users = cursor.fetchall()

        connection.close()  # Close the connection

        # Render the admin_dashboard.html with the total number of users and the user list
        return render_template('admin_dashboard.html', total_users=total_users, users=users)

    except Exception as e:
        flash(str(e))  # Display any error in the dashboard
        return redirect(url_for('admin_login'))


# Route to delete a user
@app.route('/delete_user/<int:id>', methods=['POST'])  # Use 'id' in the route parameter to match the table field
def delete_user(id):  # Use 'id' since your table has this field
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Use 'id' from the table, which is the field name in your 'users' table
        cursor.execute("DELETE FROM users WHERE id = %s", (id,))
        connection.commit()
        connection.close()

        flash("User deleted successfully!")
    except Exception as e:
        flash(str(e))  # Show any error that occurs

    return redirect(url_for('admin_dashboard'))

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            # Fetch the admin's details from the database
            cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
            admin = cursor.fetchone()

            if admin:
                # Check password hash
                if check_password_hash(admin['password'], password):
                    flash('Login successful!', 'success')
                    return redirect(url_for('admin_dashboard'))  # Redirect to the admin dashboard
                else:
                    flash('Invalid password. Please try again.', 'danger')
                    return redirect(url_for('admin_login'))  # Redirect back to login if password is wrong
            else:
                flash('Invalid username. Please try again.', 'danger')
                return redirect(url_for('admin_login'))  # Redirect back to login if username is wrong

        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'danger')
            return redirect(url_for('admin_login'))  # Redirect back to login if an exception occurs
        finally:
            cursor.close()  # Close the cursor
            connection.close()  # Close the database connection

    return render_template('admin_login.html')  # Render the admin login page for GET requests


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Extract form data
        name = request.form['name'].strip()
        dob = request.form['dob']
        gender = request.form['gender'].strip().lower()
        height = request.form['height']
        weight = request.form['weight']
        email = request.form['email'].strip()
        password = request.form['password']

        # Validate form fields (ensure none are missing)
        if not name or not dob or not gender or not height or not weight or not email or not password:
            flash('All fields are required.')
            return redirect(url_for('register'))

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Validate if email already exists in the database
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash('Email already registered. Please use a different email.')
            connection.close()  # Close connection
            return redirect(url_for('register'))

        # Hash the password using werkzeug
        hashed_password = generate_password_hash(password)

        # Insert new user into the database
        sql = "INSERT INTO users (name, dob, gender, height, weight, email, password) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (name, dob, gender, height, weight, email, hashed_password))
        connection.commit()
        connection.close()  # Close connection after commit

        flash('Registration successful! Please login.')
        return redirect(url_for('home'))  # Redirect to home page after successful registration

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            connection.close()  # Close connection

            if user and check_password_hash(user['password'], password):
                return redirect(url_for('prediction'))  # Redirect to prediction page after successful login
            else:
                flash('Invalid credentials. Please try again.')
                return redirect(url_for('home'))  # Redirect back to home page on invalid login
        except Exception as e:
            flash(str(e))
            return redirect(url_for('home'))

    return render_template('home.html')  # Render the home page for GET requests

@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    prediction_result = None
    if request.method == 'POST':
        Gender = request.form['gender']
        Age = int(request.form['age'])
        Height = int(request.form['height'])
        Weight = int(request.form['weight'])
        Duration = int(request.form['duration'])
        Heart_rate = int(request.form['heart_rate'])
        Body_temp = float(request.form['body_temp'])

        try:
            prediction_result = pred(Gender, Age, Height, Weight, Duration, Heart_rate, Body_temp)
        except ValueError as e:
            flash(str(e))

    return render_template('prediction.html', prediction=prediction_result)


@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    bmi_result = None
    category_result = None  # New variable for category
    chart_data = None
    if request.method == 'POST':
        try:
            gender = request.form['gender']
            height = float(request.form['height'])  # Height in cm
            weight = float(request.form['weight'])  # Weight in kg

            # Calculate BMI and category
            bmi_result, category_result = calculate_bmi(height, weight, gender)

            # Generate BMI chart
            chart_data = generate_bmi_chart(bmi_result)
        except ValueError:
            flash('Invalid input. Please enter valid numbers for height and weight.')
        except Exception as e:
            flash(str(e))

    return render_template('calculator.html', bmi=bmi_result, category=category_result, chart_data=chart_data)


if __name__ == '__main__':
    app.run(debug=True)
