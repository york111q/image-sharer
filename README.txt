
TITLE: Image sharer

DESCRIPTION: I hope I have completed all the tasks of the project as instructed.
I did the task by creating a new django project, I didn't use any pre-made
project. This is my first creation using django rest, so I had to learn a lot of
things to even get started. I would estimate the total time spent on the project
at about 20 hours. I didn't include the time spent learning django rest from
scratch, testing (which I haven't done before either) and making docker compose
available, so you'd have to add another 10-15 hours to that. Completing this
task showed me what I can write in django, and what I should still learn/improve.
Thank you for this opportunity.

INSTALLATION WITH DOCKER: As I'm just learning docker, I can't give you exact
instructions on how to install the project using it. I am sharing a link to the
docker repository as well as to the docker image in .tar format (added on google
drive). All the commands needed to run the project are included in the
Dockerfile.

INSTALLATION WITH PROJECT FILES: First, install all required modules using "pip
install -r requirements.txt". Then perform the migrations using "python
manage.py makemigrations" and "python manage.py migrate". Before starting the
server, run the starter.py file once, which creates accont tiers. Additionally,
you should create an administrator using "python manage.py createsuperuser", and
then you can run the server using "python manage.py runserver".

GIT: https://github.com/york111q/image-sharer.git

DOCKER CONTAINER: docker pull york111/imagesharer:latest
DOCKER IMAGE: https://drive.google.com/file/d/1w-K_g_t7IQh5_AXSP-xrSAZVv3EpIqd2/view?usp=sharing
