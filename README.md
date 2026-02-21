# Django Portfolio Website (Production Ready)

Modern portfolio platform built with Django, HTML/CSS/JS, Three.js visuals, blog publishing, signed-in comments, subscriber email notifications, and OpenAI chatbot.

## Features

- Intro, About, Education, Skills, Projects, and Contact pages
- Blog with draft/published states and admin authoring
- Signed-in user comments with moderation (`is_approved`)
- Email subscriptions with verification links
- Automatic subscriber notifications when a post is first published (Celery task)
- OpenAI chatbot widget with API rate limiting
- Render deployment blueprint with PostgreSQL + Redis + worker

## Tech Stack

- Django 5
- PostgreSQL (or SQLite locally)
- Redis + Celery
- Gmail SMTP (or any SMTP provider)
- OpenAI API
- Three.js, vanilla JavaScript, custom CSS

## Quick Start (Local)

1. Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure env:

   ```bash
   copy .env.example .env
   ```

4. Run migrations and create admin:

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. Run Django:

   ```bash
   python manage.py runserver
   ```

6. Run Celery worker (second terminal):

   ```bash
   celery -A config worker -l info
   ```

## Required Environment Variables

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `DATABASE_URL`
- `REDIS_URL`
- `EMAIL_HOST`
- `EMAIL_PORT`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `EMAIL_USE_TLS`
- `EMAIL_USE_SSL`
- `DEFAULT_FROM_EMAIL`
- `ADMIN_EMAIL`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `SITE_BASE_URL`

## Render Deployment

- Use `render.yaml` blueprint to provision:
  - Web service (`gunicorn`)
  - Worker service (`celery`)
  - Redis service
  - PostgreSQL database
- Set `DJANGO_SETTINGS_MODULE=config.settings.prod`
- Add all required environment variables in Render dashboard.
- Run migrations after deploy:

  ```bash
  python manage.py migrate
  python manage.py collectstatic --noinput
  ```

## Admin Content Setup

1. Create one `Profile` record for intro/about/hero info.
2. Add `Education`, `Skill`, and `Project` entries.
3. Create blog categories and blog posts.
4. Publish a post to trigger subscriber notification task.
5. Approve comments in admin as needed.

## Seed Resume Data Quickly

Populate the site with resume-based defaults:

```bash
python manage.py seed_resume
```

Replace existing portfolio data:

```bash
python manage.py seed_resume --replace
```

## Test Suite

Run:

```bash
python manage.py test
```
