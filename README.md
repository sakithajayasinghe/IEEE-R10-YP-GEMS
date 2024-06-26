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
   git clone https://github.com/sakithajayasinghe/IEEE-R10-YP-GEMS.git
   code IEEE-R10-YP-GEMS (open project in vscode)
   ```

2. **Create a Virtual Environment:**
   before create venv, check venv in the project folder. if you facing any issues from existing venv delete it and follow 2 & 3 steps.if not pass 2 & 3 steps.

   - **Using `venv` :**

     ```bash
     python3 -m venv venv
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
   docker pull postgres:16
   ```

2. **Start the Postgres Container:**

   ```bash
   docker run -d --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:16
   ```
3. **Go inside the postgres container**
   ```bash
   docker exec -it postgres bash
   ```
4. **Login postgres**
   ```bash
   psql -U postgres
   
   ```
5. **Create postgres Database**
   ```bash
   CREATE DATABASE project;
   
   ```
6. **exit from docker container**

7. **come to the project terminal**

**Run**
   ```
   python3 app/routes.py
   ```

8. **check logs folder for running url.**

9. **check database details**
   go inside the container
   ```bash
   docker exec -it postgres bash
   psql -U postgres project
   ```
   type -> \dt
   you can see the table

   ![Alt text](image.png)

   select * from invite_requests;


   **Screenshots**

   ![Alt text](image-1.png)

   #### use signup url to add password to the account

   ![Alt text](image-2.png)

   ![Alt text](image-3.png)

   ![Alt text](image-4.png)

   ![Alt text](image-7.png)

   ![Alt text](image-6.png)




