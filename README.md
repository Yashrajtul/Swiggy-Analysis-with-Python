# Swiggy Analysis with Python 🛵📊

A full-fledged Swiggy data analysis application built with Python and MySQL, featuring a modern GUI using `CTkinter`. This project enables interactive data visualization and insights generation from restaurant data sourced from Swiggy.

---

## 🚀 Features

- ✅ **Login & Authentication System**
- 📊 **Interactive GUI** using `CTkinter` with Swiggy-themed design
- 🗂️ **Database Integration** with MySQL for seamless data management
- 🔍 **Query Executor** with output display
- 🧾 **Schema Visualization** to explore tables and relationships
- 💾 **Data Import** functionality
- 🖼️ **Splash Screen & Screensaver** with engaging UI/UX

---

## 🏗️ Tech Stack

| Category        | Tools & Frameworks           |
|----------------|-------------------------------|
| **Frontend GUI** | Python `CTkinter`, PIL       |
| **Backend**      | Python (OOP, MySQL Connector)|
| **Database**     | MySQL                        |
| **File Handling**| CSV, Text I/O                |

---

## 📁 Project Structure

Swiggy-Analysis-with-Python/

<pre> ```bash 
  Swiggy-Analysis-with-Python/ 
  ├── db/ 
  │ └── db_connection.py 
  ├── assets/ 
  │ └── swiggy.png 
  │ └── ... 
  ├── app/ 
  │ └── app.py 
  │ └── credentials/ 
  │   └── credentials.json 
  ├── data/ 
  │ └── Swiggy_Analysis_Source_File.csv 
  ├── notebooks/ 
  │ └── swiggy_db.ipynb 
  ├── requirements.txt 
  ├── setup.sh 
  └── README.md 
  ``` </pre>

---

## ⚙️ Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Swiggy-Analysis-with-Python.git
   cd Swiggy-Analysis-with-Python

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt

4. **Configure the database**

* Update the MySQL credentials in db_connection.py
* Run provided SQL scripts (if any) to populate tables

5. **Run the application**
   ```bash
   python app/app.py

## 🧪 Modules Breakdown

| Module/File                            | Description                                                                                                                               |
| -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `db/db_connection.py`                  | Contains the `SwiggyDBConnection` class that manages database connection, initialization, disconnection, and SQL query execution.         |
| `app/app.py`                           | Main application file containing the `SwiggyApp` class, which builds the CTkinter GUI, manages navigation, and handles user interactions. |
| `data/Swiggy_Analysis_Source_File.csv` | Source CSV file used for initial data population in the database during the setup or import process.                                      |


## 🎯 Use Cases
* Students practicing database integration with GUI
* Data visualization enthusiasts interested in real-world restaurant data
* Learners exploring Python + MySQL desktop applications

## 📝 To-Do / Improvements
* Add graph visualizations (matplotlib/seaborn)
* Export query result as Excel



## Screenshots

### Splash Screen

![Splash Screen](image.png)

### Login Page

![Login Screen](image-1.png)

### Swiggy Data Analysis Dashboard

![Swiggy Data Analysis Dashboard](image-2.png)

### Show Schema Page

![Show Schema Page](image-3.png)

### Fetch Table Data Page

![Fetch Table Data Page](image-4.png)

### Run Custom SQL Query

![Run Custom SQL Query](image-5.png)

## Setup
