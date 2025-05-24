# Social Website Project

Welcome to the Social Website project! This Django-based website is designed to bring social features to life, allowing users to connect, share images, and interact with each other. In this project, we will cover a wide range of functionalities, from user registration and authentication to profile management and social interactions.

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [Features](#features)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Introduction
In this project, we aim to build a fully-fledged social website using Django. The project focuses on the following key features:

- User Registration and Authentication
- Password Management
- User Profiles
- Media File Uploads
- User Activity Feeds
- User Interactions (like/unlike, follow/unfollow)
- Bookmarking Images

## Installation
To set up and run this project on your local machine, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/GasimV/Django-Social-Website.git
   ```

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```
   python manage.py migrate
   ```

4. Start the development server:
   ```
   python manage.py runserver
   ```

5. Access the website at `http://localhost:8000/` in your web browser.

## Features
- **User Registration:** Users can sign up for an account with a unique email and password.

- **Authentication:** Utilizing Django's authentication framework for secure user login and logout.

- **Password Management:** Users can change their passwords and reset them if forgotten.

- **User Profiles:** Extend the user model with a custom profile model for additional user information.

- **Media File Uploads:** Users can upload and share images on the platform.

- **Activity Feeds:** Users can see activity from the users they follow, such as posts and likes.

- **User Interactions:** Users can like and unlike images, follow and unfollow other users.

- **Bookmarking Images:** Users can bookmark and share images from the internet.

## Usage
This project provides a foundation for building a social website. You can use it as a starting point and extend it to add more features or customize it to fit your specific requirements. To get started, follow the installation instructions mentioned above.

## Contributing
We welcome contributions from the community. If you'd like to contribute to this project, please fork the repository, make your changes, and submit a pull request. You can also report issues or suggest improvements in the GitHub issues section.

## License
This project is based on the concepts and code examples from the book "Django 4 By Example, Fourth Edition," published by Packt Publishing. The book is copyrighted by Packt Publishing, and all rights are reserved by the publisher.

Please note that while this project is open-source and available for use and modification, it is subject to the copyright terms set by the book's publisher. Any usage of this project should be in accordance with the copyright and licensing terms specified in the book.

For more information on the book's copyright and licensing terms, please refer to the book "Django 4 By Example, Fourth Edition," ISBN 978-1-80181-305-1, and visit the publisher's website at www.packt.com.

Please ensure that you comply with the book's copyright and licensing terms when using or distributing this project.

Thank you for using and contributing to the Social Website project! We hope it helps you build amazing social platforms with Django.