# DBMS Query Execution Plan

## Project Overview
The broad aims of the project are as follows:
- Retrieve and visualize the QEP of a given SQL query.
- Support what-if queries on the QEP by enabling interactive modification of the physical operators and join order in the visual tree view of the QEP to generate an AQP.
- Retrieve the estimated cost of the AQP and compare its cost with the QEP.

## ERD
<img src="images/ERD.svg" alt="ERD" width="600"></img>

## Prerequisites
- Python 3.10
- pip (Python package installer)
- Git LFS (Large File Storage) - [Download](https://git-lfs.github.com/)
- PostgreSQL Server - [Download](https://www.postgresql.org/download/)

## Setup Instructions

### 1. Install Git LFS
Download and install Git LFS from the link provided above

### 2. Initialize Git LFS
Run the following command to initialize Git LFS
```sh
git lfs install
```

### 3. Clone the Repository
```sh
git clone https://github.com/xeroxis-xs/DBMS-QueryExecutionPlan-Python.git
cd DBMS-QueryExecutionPlan-Python
```

### 4. Create a Virtual Environment
```sh
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 5. Install the Required Packages
Install the required Python packages using `pip`.
```sh
pip install -r requirements.txt
```

### 6. Check if PostgreSQL is Installed
Run the following command to check if PostgreSQL is installed.
```sh
postgres --version
```

### 7. Start the PostgreSQL Server
Start the PostgreSQL server by starting ```pgAdmin``` app or running the following command.

**MacOS**:
```sh
sudo service postgresql start
```
**Windows**:

Go to start > Services > postgresql-x64 > Start

### 8. Connect to your PostgreSQL Server
In `pgAdmin`, select the default `PostgreSQL 17` server and connect to it.

Alternatively, use the following command to connect to the default server.
```sh
psql -U <your_username> -h localhost -p <your_port>
```

### 9. Create a new Database
Create a new database via the PostgreSQL command line or pgAdmin.
```sh
CREATE DATABASE your_database_name;
```

### 10. Set Up the `.env` File
Create a new file named `.env` in the root directory of the project and add the following environment variables.
```sh
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=your_port  # Default PostgreSQL port is 5432
```

### 11. Populate the Database
Run the following command to populate the database with the required tables and data.
```sh
python -m db.populate
```

### 12. Run the Project
Execute the main script to populate the database and start the project.
```sh
python -m project
```

Or, if you are using PyCharm, you can click on the green play button in the top right corner of the editor.  
<img src="images/img.png" alt="Run in PyCharm" width="300"></img>