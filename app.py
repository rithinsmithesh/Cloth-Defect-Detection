from flask import Flask, request, render_template, redirect, url_for, session, flash
import tensorflow as tf
import numpy as np
import cv2
import mysql.connector
import os
from werkzeug.utils import secure_filename


# Load trained model for Fabric Classification & Quality Grading


app = Flask(__name__)
app.secret_key = "supersecretkey"
app.config['UPLOAD_FOLDER'] = 'static/uploads'

model = tf.keras.models.load_model("fabric_defect_model.h5")
videos_model = tf.keras.models.load_model("video_fabric_defect_model.h5")

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# MySQL Database Configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "fabric_marketplace"
}

def connect_db():
    return mysql.connector.connect(**db_config)

# Home Page
@app.route("/")
def home():
    return render_template("index.html")

# User Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)", 
                       (name, email, password, role))
        connection.commit()
        cursor.close()
        connection.close()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))
    
    return render_template("register.html")

# User Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Admin Default Credentials
        if email == "admin@gmail.com" and password == "admin":
            session["user_id"] = 0
            session["role"] = "admin"
            session["name"] = "Administrator"
            flash("Admin login successful!", "success")
            return redirect(url_for("admin_dashboard"))

        connection = connect_db()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        connection.close()

        if user:
            session["user_id"] = user["id"]
            session["role"] = user["role"]
            session["name"] = user["name"]

            if user["role"] == "buyer":
                return redirect(url_for("buyer_dashboard"))
            elif user["role"] == "seller":
                return redirect(url_for("seller_dashboard"))
        else:
            flash("Invalid credentials. Please try again.", "danger")

    return render_template("login.html")


# Define class labels
categories = ["Defect Cloth", "Good Cloth"]

def predict_fabric(image_path):
    """ Predicts whether the cloth is good or has a defect using the trained model """
    img = cv2.imread(image_path)
    img = cv2.resize(img, (128, 128))
    img = np.expand_dims(img / 255.0, axis=0)
    
    prediction = model.predict(img)
    predicted_class_index = np.argmax(prediction)
    predicted_class = categories[predicted_class_index]
    confidence = np.max(prediction) * 100

    # Assign quality grade based on confidence
    if confidence >= 80:
        grade = "A"
    elif 50 <= confidence < 80:
        grade = "B"
    else:
        grade = "C"

    # Generate final output message
    if predicted_class == "Good Cloth":
        final_output = "This is a Good Cloth ✅"
    elif predicted_class == "Hole":
        final_output = "This is a Defect Cloth with a Hole ❌"
    else:
        final_output = "This is a Defect Cloth ❌"
    
    # Do not show grade if it's a defect cloth
    if final_output == "This is a Defect Cloth ❌":
        return final_output, confidence, None  # No grade for defect cloth
    
    return final_output, confidence, grade  # Return grade for non-defect cloth

@app.route("/predict_fabric", methods=["POST"])
def predict_fabric_route():
    """ Buyer uploads an image, and the model predicts fabric condition """
    if "file" not in request.files:
        flash("No file uploaded!", "danger")
        return redirect(url_for("buyer_dashboard"))

    file = request.files["file"]
    if file.filename == "":
        flash("No selected file!", "danger")
        return redirect(url_for("buyer_dashboard"))

    if file:
        # Save uploaded file
        filename = file.filename
        file_path = os.path.join("static/uploads", filename)
        file.save(file_path)

        # Get AI prediction
        final_output, confidence, grade = predict_fabric(file_path)  # Ensure 4 values are unpacked

        return render_template("buyer_dashboard.html", name=session.get("name", "Buyer"), 
                                final_output=final_output, 
                               confidence=confidence, grade=grade, uploaded_filename=filename)

def extract_frames(video_path, output_folder, frame_interval=10):
    """ Extract frames from video """
    os.makedirs(output_folder, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    success, frame = cap.read()
    
    while success:
        if frame_count % frame_interval == 0:
            frame_filename = os.path.join(output_folder, f"frame_{frame_count}.jpg")
            cv2.imwrite(frame_filename, frame)
        success, frame = cap.read()
        frame_count += 1
    cap.release()

def predict_fabric_from_video(video_path):
    """ Predicts if fabric in video is Defect or Non-Defect Cloth """
    temp_folder = "TempFrames"
    os.makedirs(temp_folder, exist_ok=True)
    extract_frames(video_path, temp_folder, frame_interval=10)  # Extract frames
    
    defect_detected = False  # Flag to track defect detection
    
    for frame in os.listdir(temp_folder):
        frame_path = os.path.join(temp_folder, frame)
        img = cv2.imread(frame_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to RGB
        img = cv2.resize(img, (128, 128))
        img = np.array(img, dtype="float32") / 255.0
        img = np.expand_dims(img, axis=0)
        
        prediction = videos_model.predict(img)
        print(f"Prediction Raw Value: {prediction[0][0]}")  # Debugging
        
        threshold = 0.5  # Adjustable threshold
        if prediction[0][0] <= threshold:
            defect_detected = True  # Mark as defect
            detect_defects(frame_path)  # Mark defects
    
    # Clean up
    for file in os.listdir(temp_folder):
        os.remove(os.path.join(temp_folder, file))
    os.rmdir(temp_folder)
    
    return "Defect Cloth ❌" if defect_detected else "Non-Defect Cloth ✅"

def detect_defects(image_path):
    """ Detect defects (holes, cuts) and highlight with red circles """
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        if cv2.contourArea(contour) > 500:  # Adjust threshold
            (x, y), radius = cv2.minEnclosingCircle(contour)
            center = (int(x), int(y))
            radius = int(radius)
            cv2.circle(img, center, radius, (0, 0, 255), 5)  # Red Circle
    
    output_path = image_path.replace(".jpg", "_marked.jpg")
    cv2.imwrite(output_path, img)
    
    return output_path

@app.route("/predict_fabric_video", methods=["POST"])
def predict_fabric_video():
    """ Buyer uploads a video, and the model predicts fabric condition """
    if "file" not in request.files:
        flash("No file uploaded!", "danger")
        return redirect(url_for("buyer_dashboard"))

    file = request.files["file"]
    if file.filename == "":
        flash("No selected file!", "danger")
        return redirect(url_for("buyer_dashboard"))

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        results = predict_fabric_from_video(file_path)
        return render_template("buyer_dashboard.html", name=session.get("name", "Buyer"), results=results, uploaded_filename=filename)

# Buyer Dashboard
@app.route("/buyer")
def buyer_dashboard():
    if "user_id" not in session or session["role"] != "buyer":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))

    connection = connect_db()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT f.*, u.name AS seller_name, u.email AS seller_email FROM fabrics f JOIN users u ON f.seller_id = u.id")
    fabrics = cursor.fetchall()

    # Predict fabric type and quality for each fabric
    for fabric in fabrics:
        image_path = os.path.join("static/uploads", fabric["image"])
        fabric["predicted_fabric"], fabric["predicted_defect"], fabric["quality_grade"] = predict_fabric(image_path)

    cursor.close()
    connection.close()

    return render_template("buyer_dashboard.html", name=session["name"], fabrics=fabrics)


# Seller Dashboard
@app.route("/seller")
def seller_dashboard():
    if "user_id" not in session or session["role"] != "seller":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))

    connection = connect_db()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM fabrics WHERE seller_id = %s", (session["user_id"],))
    fabrics = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("seller_dashboard.html", name=session["name"], fabrics=fabrics)

@app.route("/add_fabric", methods=["POST"])
def add_fabric():
    if "user_id" not in session or session["role"] != "seller":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))
    
    name = request.form["name"]
    price = request.form["price"]
    fabric_type = request.form["type"]
    
    file = request.files["image"]
    if file:
        image_filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
        file.save(file_path)
        
        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO fabrics (name, type, price, image, seller_id) VALUES (%s, %s, %s, %s, %s)", 
                       (name, fabric_type, price, image_filename, session["user_id"]))
        connection.commit()
        cursor.close()
        connection.close()
        
        flash("Fabric added successfully!", "success")
    
    return redirect(url_for("seller_dashboard"))

# Delete Fabric (Seller)
@app.route("/delete_fabric/<int:fabric_id>")
def delete_fabric(fabric_id):
    if "user_id" not in session or session["role"] != "seller":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))

    connection = connect_db()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM fabrics WHERE id = %s AND seller_id = %s", (fabric_id, session["user_id"]))
    connection.commit()
    cursor.close()
    connection.close()

    flash("Fabric deleted successfully!", "success")
    return redirect(url_for("seller_dashboard"))

# Admin Dashboard
@app.route("/admin")
def admin_dashboard():
    if "user_id" not in session or session["role"] != "admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("login"))

    connection = connect_db()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.execute("SELECT * FROM fabrics")
    fabrics = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template("admin_dashboard.html", users=users, fabrics=fabrics)

# Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
