---

# Django E-Learning Platform

## Project Overview

This project is a comprehensive e-learning platform built with Django. It includes a fully functional content management system (CMS) for managing courses, modules, and content, as well as a student enrollment and registration system. Additionally, it integrates advanced features such as caching, a RESTful API, and real-time chat capabilities using Django Channels.

The platform is highly modular, making use of reusable components and Django best practices to ensure scalability, maintainability, and performance. It also features a production-ready environment using Docker, NGINX, and PostgreSQL.

## Key Features

### 1. **Content Management System (CMS)**
   - Instructors can create and manage courses and their content with ease.
   - Supports diverse content types including text, images, videos, and documents.
   - Built with class-based views (CBVs) and mixins for modularity and reusability.
   - Includes a drag-and-drop interface for ordering course modules and content.

### 2. **Student Registration and Enrollment**
   - Students can register for an account and enroll in available courses.
   - Provides public views for browsing courses and their contents.
   - Enrollment management system for instructors to handle student access.

### 3. **Rendering and Caching Content**
   - Efficient rendering of various content types (text, videos, documents) for course modules.
   - Integrates Django’s caching framework to improve performance and reduce database load.
   - Uses Memcached and Redis backends for high-performance caching.

### 4. **RESTful API**
   - Provides a fully functional API using Django REST framework (DRF).
   - Includes serializers for all core models and supports nested serializers.
   - Implements ViewSets, routers, and custom API views.
   - Handles API authentication and custom permissions for secure access.
   - Allows external applications to consume API data for integration with other platforms (e.g., mobile apps).

### 5. **Real-Time Chat Server**
   - Implements real-time messaging for students within course chat rooms using Django Channels.
   - WebSocket support for asynchronous communication and real-time updates.
   - Redis-powered channel layers for handling message broadcasting.
   - Persists chat messages into the database for chat history and improved user experience.

### 6. **Production-Ready Environment**
   - Configures Django settings for multiple environments (development, production).
   - Utilizes Docker Compose for orchestrating services such as PostgreSQL, Redis, and NGINX.
   - Serves static and media files through NGINX for efficient handling.
   - Secures the application with TLS/SSL via NGINX, ensuring secure connections.
   - Optimizes performance and scalability through the use of the ASGI server (Daphne) for Django Channels.

## Technologies Used

- **Django**: Web framework for building the e-learning platform.
- **Django REST framework (DRF)**: For creating the API.
- **Django Channels**: For real-time chat functionality.
- **PostgreSQL**: Database management system.
- **Redis**: For caching and asynchronous communication.
- **Memcached**: For high-performance caching.
- **NGINX**: For serving static and media files.
- **Docker & Docker Compose**: For containerizing the application and managing services.

---

## License

See the [LICENSE](https://github.com/PacktPublishing/Django-5-By-Example/tree/main/Chapter12) file for more information.