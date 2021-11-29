# Laboratory Information Management System <br>
Created by Dennis Lin <br>

## Description <br>
This web app is used to track the lifecyle of a sample through a research laboratory.

## Environment <br>
Python 3 Version: 3.9.7 <br>
Django Version: 3.2.7

## Project Setup Instructions <br>
In terminal: <br>
1. > django-admin startproject mysite

Place all folders and files inside LIMS into the root directory. Example shown below <br>
![image](https://user-images.githubusercontent.com/48298105/142499446-15ea4ebe-b686-4ce4-bd36-07d0343a3b1d.png)

2. > urls.py modification changes should be as follows:
![image](https://user-images.githubusercontent.com/48298105/142498476-9b13b3fb-d7f2-426d-89b9-f928dd7c5906.png)

3. > Include the LIMS app in the settings.py file. <br>
![image](https://user-images.githubusercontent.com/48298105/142498675-eaa7ae17-cecf-471f-8389-7b08e5085bae.png)

In terminal <br>

4. > python3 manage.py makemigrations <br>
5. > python3 manage.py migrate
6. > python3 manage.py createsuperuser 

Continue answering all of the prompts until you are successful in creating an admin account.

## Deploying the server locally
In terminal

> python3 manage.py runserver
![image](https://user-images.githubusercontent.com/48298105/142499744-56b282ad-00e5-4bdc-a81b-6b578dd4dfc4.png)

Navigate to the address displayed in terminal in browser (ex. Chrome)

# Emailing

Emailing is set up through Google Account services. You would need to be able to create an app password and save your email and app password inside the Database via Django admin console with the identifier 'EmailNotification'

Email address: 'example@gmail.com'

Email Password: Google App Password (not your login password)

# Home Page
![image](https://user-images.githubusercontent.com/48298105/143933788-8b47db30-b9ab-423a-ba26-ae4dadc1b8a5.png)

# Login Page
![image](https://user-images.githubusercontent.com/48298105/143934042-4fda2b3b-952d-47ba-88b1-029f5a85868f.png)

![image](https://user-images.githubusercontent.com/48298105/143933948-d5968096-dbdb-4af1-910f-a2874829dcf2.png)

# Register an Account
![image](https://user-images.githubusercontent.com/48298105/143934137-613831c6-31a6-4e31-b330-437ac0f4c2af.png)

# Home Page (with Login)
![image](https://user-images.githubusercontent.com/48298105/143934890-efaa29a2-72b6-461a-a18e-3e203545b6c8.png)

