# Glowingmane

#### Video Demo:  <https://youtu.be/_UiyQz2gPb0>
## Description:
Welcome to GlowingMane.
<img width="1452" alt="Screenshot 2023-12-13 at 14 50 08" src="https://github.com/Shorla/glowingmane.github.io/assets/77856859/ee75a5d9-48a9-410c-b35e-e56fa04a2abc">




GlowingMane embraces the diversity of hair, acknowledging natural curls, sleek straight locks, colored strands, and all variations. This project aims to provide a unique approach to hair care for every user.

GlowingMane is accessible to all users, free of charge. Commence your journey to vibrant, healthy hair by clicking the 'Calculate My Hair Growth' button, exploring the tool, or learning more about GlowingMane.

## PROJECT STRUCTURE:
The Glowing Mane app is crafted using HTML, CSS, Javascript, and Bootstrap for the frontend; Python and Flask for the backend; and Sqlite3 for the database. The project folder structure encompasses various elements, including static folders for images and CSS, a templates folder housing the HTML files, and Python files such as app.py and helpers.py. The heart of it all lies in the calculator.html file, our calculator, taking in user's input and returning estimated hair length or average monthly growth depending on their request.
NOTE: The calculator.db contains sample data for testing purposes.

## HOW TO USE THE APPLICATION
Navigating through the eight pages of the application begins with the homepage, offering basic information about Glowing Mane. The About page delves deeper into our team, mission, and available support. Our blog page features a wealth of articles on hair care. The signup page allows users to register, leading to the login page, granting access to both the calculator and logout page. The calculator, the centerpiece of our website, consists of two forms. The first calculates the average monthly hair growth based on the last four months' input, while the second compares the latest input to the expected length, providing personalized commendations.

## Features
#### Users can:

* read blogs about hair care.
* Sign in/Sign up on the app
* calculate their average monthly hair growth
* compare their current hair growth to the estimated hair growth generated.
NOTE: The calculator page can only be accessed by registering and logging in to the website.
If you don't want to register an account,
You can login with Username - Olushorla Password - 12345

### Running the application locally
This application can be used through:
* Github codespace
* on your local machine

#### Github codespaces

STEPS:
* Fork the repository
* On the forked repository, click on the code button in green.
* click on codespaces and select "open in a codespace".
* After the codespace is opened, on the terminal, install the following:

```
pip install flask
pip install flask-session
pip install cs50

```
Note: If you are getting "pip not found" error, use pip3 for the installations.

* use ```flask run``` to start the application.
* copy and paste the generated url to your browser!

#### Local Machine

STEPS:
* Fork the repository
* On the forked repository, click on the code button in green.
* click on Local and copy the generated link.
* On your terminal, type "git clone" followed by the generated link.
* After successful cloning, open the folder on the IDE of your choice.
* After, the folder is opened, on the terminal in your IDE, install the following:

```
pip install flask
pip install flask-session
pip install cs50

```
Note: If you are getting "pip not found" error, use pip3 for the installations.

* use ```flask run``` to start the application.
* copy and paste the generated url to your browser!

### Running the application online
Visit the url: http://shorla.pythonanywhere.com
You can login with Username - Olushorla Password - 12345


## Motivation
Since childhood, I had to cut my hair because my mother wasn't familiar with caring for its unique texture. Fast forward to adulthood, my attempts to grow it out were met with challenges and damaged hair. Three years ago, I decided to start anew with a blend of research and a solid regimen, turning my hair care journey into a success. This personal experience fueled my passion for hair care and a desire to assist others. Recognizing gaps in the industry, particularly in accountability and record-keeping, led to the creation of the GlowingMane app.

## Contributing

This is an Open source project, hence, contributions are appreciated. This is only the first version, so, several improvements and adjustments will take place over the years. The goal is to make everyone have access to good hair care through accurate measurements, record keeping, and a good regimen.
