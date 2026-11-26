#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'placement.settings')

    # If running on Render (or if PORT is defined) and 'runserver' is invoked,
    # launch gunicorn bound to 0.0.0.0:$PORT, or bind runserver to 0.0.0.0:$PORT.
    if len(sys.argv) > 1 and sys.argv[1] == 'runserver':
        is_render = (
            os.environ.get('RENDER')
            or os.environ.get('RENDER_EXTERNAL_HOSTNAME')
            or os.environ.get('RENDER_SERVICE_ID')
        )
        port = os.environ.get('PORT')
        if is_render or port:
            bind_port = port if port else '10000'
            import shutil
            import subprocess

            # Run migrations & collect static files safely as pre-launch step
            try:
                subprocess.run([sys.executable, sys.argv[0], 'migrate', '--noinput'], check=False)
                subprocess.run([sys.executable, sys.argv[0], 'collectstatic', '--noinput'], check=False)
            except Exception:
                pass

            # Try launching production gunicorn server
            try:
                gunicorn_bin = shutil.which('gunicorn')
                if gunicorn_bin:
                    os.execv(
                        gunicorn_bin,
                        [
                            'gunicorn',
                            'placement.wsgi:application',
                            '--bind',
                            f'0.0.0.0:{bind_port}',
                        ],
                    )
                else:
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
                pass

            # Fallback for runserver: guarantee it binds to 0.0.0.0 instead of 127.0.0.1
            has_binding = any(':' in arg for arg in sys.argv[2:])
            if not has_binding:
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
