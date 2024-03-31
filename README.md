## project plan design

[https://drive.google.com/drive/folders/1hTTHVyi-rLBTHSJO6smHObB6cZ7134lN?usp=sharing]

**Getting Started**

This project provides a streamlined setup process to get you up and running quickly.
Operating system Ubuntu.Please use ubuntu os.

**Prerequisites**

- Python 3.10.12 ([https://www.python.org/downloads/](https://www.python.org/downloads/))

**Project Setup**

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/<your-username>/<your-project-name>.git
   cd IEEE-R10-YP-GEMS
   ```

2. **Create a Virtual Environment:**

   It's highly recommended to create a virtual environment.

   - **Using `venv` :**

     ```bash
     python -m venv venv
     source venv/bin/activate  # Linux
     ```

3. **Install Project Dependencies:**

   Install the required Python packages listed in the `requirements.txt` file:

   ```bash
   pip install -r requirements.txt
   ```

4. **Install Docker :**

   - **Linux/macOS:** Follow the official installation instructions for your distribution ([https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)).

**Database Setup (Using Docker)**

1. **Pull the Postgres Image:**

   ```bash
   docker pull postgres
   ```

2. **Start the Postgres Container:**

   ```bash
   docker run -d --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:16
   ```

**Connect to Postgres Container (Optional)**

1. **Enter the Container's Shell :**

   ```bash
   docker exec -it postgres bash
   ```

2. **Create a Database:**

   ```sql
   psql -U postgres
   CREATE DATABASE project;
   ```

3. **Run**
   ```
   python3 app/routes.py
   ```
