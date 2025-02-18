# Instagram Media Downloader

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Django](https://img.shields.io/badge/django-4.2.9-green)
![Last Updated](https://img.shields.io/badge/last%20updated-2025--02--18-brightgreen)

A high-performance, scalable Instagram media downloader built with Django. This project allows downloading photos, videos, and carousel posts from Instagram without requiring authentication.

## Features

- 🚀 High-performance asynchronous downloads
- 📊 Real-time progress tracking
- 🎯 Support for photos, videos, and carousel posts
- 🔄 Automatic retry mechanism for failed downloads
- 📁 Organized media storage with cleanup
- 🔒 Rate limiting and security features
- 📱 Responsive web interface
- 🖥️ RESTful API
- 📈 Download analytics and tracking
- 🔍 Media validation and verification

## Technology Stack

- **Backend**: Django 4.2.9, Django REST Framework
- **Database**: PostgreSQL
- **Caching**: Redis
- **Task Queue**: Celery
- **Web Server**: Nginx, Gunicorn
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Container**: Docker, Docker Compose
- **Media Processing**: yt-dlp, Pillow
- **Testing**: pytest, coverage
- **CI/CD**: GitHub Actions

## Prerequisites

- Python 3.9+
- Docker and Docker Compose
- PostgreSQL 13+
- Redis 6+

## Project Structure

```text
instagram_downloader/
├── core/                      # Django project core
│   ├── settings/             # Settings modules
│   │   ├── base.py          # Base settings
│   │   ├── development.py   # Development settings
│   │   └── production.py    # Production settings
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py              # WSGI configuration
├── downloader/               # Main application
│   ├── api/                 # API endpoints
│   ├── services/            # Business logic
│   ├── tasks/               # Celery tasks
│   ├── templates/           # HTML templates
│   └── utils/               # Utility functions
├── static/                  # Static files
├── media/                   # Media storage
├── tests/                   # Test suite
├── scripts/                 # Utility scripts
├── docker/                  # Docker configuration
├── requirements/            # Python dependencies
└── manage.py               # Django management script
```
