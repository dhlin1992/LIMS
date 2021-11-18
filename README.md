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
