# Phishing Website
## Describe
- This is a website used to detect phishing URLs
- The website uses input including screenshots and features extracted from the URL to detect phishing URLs.
- Using deep learning and object detection algorithms.

## Group member information 
|Id|Full name|Student ID|Role|
|-|-|-|-|
|1|Lê Tôn Nhân|19520199|Research, Design, Dev|
|2|Lâm Thanh Ngân|19521884|Research, Design, Dev|
## Environment settings
- First, Open tempinal on vscode
- Execute the command `python -m venv venv`
- Execute file: /venv/Scripts/activate.bat to enter the environment
- Install some required packages to use django:
     - pip install -U wheel
     - pip install django
## Commands needed to create the project
- Create a new project
> django-admin startproject MyProject
- Create a new app
> python manage.py startapp MainApp
- Check changes in cached database
> python manage.py makemigrations
- Save database
> python manage.py migrate
- Run server
> python manage.py runserver
- Install superuser (admin/admin)
> python manage.py createsuperuser
## Some extra packages
> pip install icecream
> pip install django-ckeditor
> pip install django-mathfilters

### User admin to manage:
- Username: admin
- Password: admin
### Regular User:
- Username: nhalee
- Pass: Nhanle1234@

## Function brief description

- Login, register: Perform escape of inputs, for username use regex to check including only characters from a-z, A-Z, 0-9, check email is valid or not use function validate_email powered by django
- User authorization (supported by django): Admin will have the right to delete the url to delete the user ..., and the user only has the right to view and check the phishing url
- form: Use csrf_token supported by django to avoid csrf attack
