# facial-rec-software
Facial Recognition software used for user authentication and login. 

Using opencv library and face_recognition in conjunction to open a website running on the flask framework.

User will either get the option to log in or create a new user.

If User chooses login, they will land on a page that asks for their username(email), opencv will then open a window within the webpage with a view of their webcam.

In the backend, the username should already have an encoding of the users face stored in the back-end, it will then recognize them and land them into the homepage successfully.

If the face shown does that match that which is encoded for the username, you will receive a prompt asking you to input your password instead, which is also stored in the backend.

Backend will run on MongoDB due to its ability to retain structured, semi-structured and unstructured data. I've tried to consider scaling but haven't yet found a solution considering storing image isn't common practice, but storing the encoding itself makes more sense since its just an array of numerical values. 

Will look into CDN for image storage instead or possibly just try to upload a url of the image and then process it afterwards. 


