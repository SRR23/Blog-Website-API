
# Blog API

This is a RESTful API for a blog platform built with Django and Django Rest Framework (DRF). The API allows users to create, read, update, and delete blog posts, add favourite post, comment on posts, and manage user authentication.


## Features
- User authentication (registration, login)
- CRUD operations for blog posts
- Comment and rating system for posts
- add to favourite functionality
- Search and filtering for posts
- Token-based authentication

## Installation

Follow these steps to set up and run the project locally:


    1. Clone the Repository

    First, clone the repository from GitHub:

    git clone https://github.com/SRR23/Blog-Website-API.git
    cd config

    2. Set Up a Virtual Environment
    Create and activate a virtual environment:

    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # On Windows
    python -m venv venv
    venv\Scripts\activate

    3. Install Dependencies
    Install the required packages:

    pip install -r requirements.txt

    4. Apply Migrations
    Run database migrations:

    python manage.py migrate

    5. Create a Superuser (Optional)
    To access the Django admin panel, create a superuser:

    python manage.py createsuperuser
    Follow the prompts to set up your admin account.

    6. Run the Development Server
    Start the Django development server:

    python manage.py runserver
    The API will be available at:
    📌 http://127.0.0.1:8000/
    
## API Endpoints
    Authentication:
        POST	/api/register/
        POST	/api/login/

    User Profile:
        GET /api/profile/ # Get Profile
        PUT /api/profile/{id}/ # Update Profile

    Blog Management:
        POST /api/blogs/ # Create a Blog
        GET /api/blogs/ # Show My Blogs
        PUT /api/blogs/{id}/ # Update One of My Blogs
        DELETE /api/blogs/{id}/ # Delete One of My Blogs
    
    Favourite Blogs:
        POST /api/favourites/{id}/ # Add Blog to Favourite
        GET /api/favourites/ # Show My Favourite List
        DELETE /api/favourites/{id}/ # Remove From Favourite
    
    Reviews:
        POST /api/blog-detail/{slug}/ # Comment and Rating
    
    Blog Listing & Filtering:
        GET /api/all-blogs/?latest={number} # Show Some Blogs in Home
        GET /api/all-blogs/ # Show All Blogs
        GET /api/blog-detail/{slug}/ # Show Blog Detail
        GET /api/search/?find={query} # Search Blog by Title or Tag
        GET /api/filter-category/?category={id} # Filter Blogs by Category
        GET /api/filter-tags/?tags={tag} # Filter Blogs by Tag
    
    Blog Metadata:
        GET /api/tags/ # List All Tags
        GET /api/categories/ # List All Categories

## Authentication
    This API uses JWT-based authentication. To access protected routes, include your token in the request headers:
    Authorization: Bearer your_token_here
    
## Technologies Used
    Python
    Django
    Django Rest Framework (DRF)
    SQLite
    JWT Token Authentication
