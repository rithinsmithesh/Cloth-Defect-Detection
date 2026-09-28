# 🧵 Cloth Defect Detection

A Flask-based web application that integrates **Deep Learning (CNN)** and **Computer Vision** to automatically detect fabric defects from images and videos. The system provides a secure online marketplace where **Buyers**, **Sellers**, and **Administrators** can manage fabric products while using AI for quality inspection.

---

## 📌 Project Features

- 🔐 User Authentication (Buyer, Seller & Admin)
- 👤 User Registration & Login
- 🛍️ Fabric Marketplace
- 📤 Fabric Image Upload
- 🎥 Fabric Video Upload
- 🤖 AI-Based Fabric Defect Detection
- ✅ Good Cloth / Defect Cloth Classification
- 🗄️ MySQL Database Integration
- 📊 Role-Based Dashboards

---

# 🛠️ Technologies Used

| Category | Technologies |
|----------|--------------|
| Programming Language | Python |
| Backend | Flask |
| Frontend | HTML, CSS, Bootstrap, JavaScript |
| Database | MySQL |
| Deep Learning | TensorFlow, Keras |
| Computer Vision | OpenCV |
| Model | Convolutional Neural Network (CNN) |

---

# 📂 Project Structure

```text
Cloth-Defect-Detection/
│
├── app.py
├── requirements.txt
├── fabric_defect_model.h5
├── video_fabric_defect_model.h5
├── database.sql
├── static/
│   ├── uploads/
│   └── images/
├── templates/
└── README.md
```

---

# ⚙️ Installation & Setup

## Step 1: Clone the Repository

```bash
git clone https://github.com/rithinsmithesh/Cloth-Defect-Detection.git
```

Move into the project folder:

```bash
cd Cloth-Defect-Detection
```

---

## Step 2: Create a Virtual Environment (Recommended)

Windows

```bash
python -m venv venv
```

Activate the environment

```bash
venv\Scripts\activate
```

---

## Step 3: Install Required Packages

```bash
pip install -r requirements.txt
```

---

## Step 4: Configure MySQL

Create a database named:

```sql
fabric_marketplace
```

Import the SQL file (`database.sql`) using MySQL Workbench or phpMyAdmin.

---

## Step 5: Configure Database Connection

Open `app.py` and update the database configuration:

```python
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "YOUR_PASSWORD",
    "database": "fabric_marketplace"
}
```

Replace **YOUR_PASSWORD** with your MySQL password.

---

## Step 6: Run the Application

```bash
python app.py
```

---

## Step 7: Open the Application

Open your browser and visit:

```text
http://127.0.0.1:5000
```

---

# 👨‍💼 Default Admin Login

| Email | Password |
|--------|----------|
| admin@gmail.com | admin |

---

# 🔄 Project Workflow

```text
User Login / Registration
          │
          ▼
Upload Fabric Image / Video
          │
          ▼
Image Preprocessing (OpenCV)
          │
          ▼
CNN Model Prediction
(TensorFlow / Keras)
          │
          ▼
Good Cloth / Defect Cloth
          │
          ▼
Display Result
          │
          ▼
Store Data in MySQL
```

---

# 🧠 AI Model

- Model: Convolutional Neural Network (CNN)
- Framework: TensorFlow & Keras
- Image Processing: OpenCV
- Input: Fabric Images / Video Frames
- Output:
  - ✅ Good Cloth
  - ❌ Defect Cloth

---

# 👥 User Modules

### Buyer
- Register & Login
- View Available Fabrics
- Upload Image for AI Prediction
- Upload Video for AI Prediction
- View Prediction Results

### Seller
- Login
- Add Fabric Products
- Upload Fabric Images
- Manage Products
- Delete Products

### Admin
- Login
- View Users
- View Fabrics
- Monitor Marketplace

---

# 🚀 Future Enhancements

- Multi-class defect detection
- Real-time camera inspection
- Mobile application support
- Cloud deployment
- Explainable AI (XAI)
- Improved model accuracy with larger datasets

---

# 👨‍💻 Author

**Murahari Rithin Smithesh**



---

## ⭐ If you found this project useful, consider giving it a Star!
