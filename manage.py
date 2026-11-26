#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'placement.settings')

    # If running on Render and 'runserver' is invoked, automatically run migrations,
    # collect static files, and launch gunicorn bound to 0.0.0.0:$PORT
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        is_render = os.environ.get('RENDER') or os.environ.get('RENDER_EXTERNAL_HOSTNAME')
        port = os.environ.get('PORT')
        if is_render or port:
            bind_port = port if port else '10000'
            import subprocess
            try:
                subprocess.run([sys.executable, sys.argv[0], 'migrate', '--noinput'], check=False)
                subprocess.run([sys.executable, sys.argv[0], 'collectstatic', '--noinput'], check=False)
            except Exception:
                pass

            try:
                os.execv(
                    sys.executable,
                    [
                        sys.executable,
                        '-m',
                        'gunicorn',
                        'placement.wsgi:application',
                        '--bind',
                        f'0.0.0.0:{bind_port}',
                    ],
                )
            except Exception:
                if len(sys.argv) == 2:
                    sys.argv.append(f'0.0.0.0:{bind_port}')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
