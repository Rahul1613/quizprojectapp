import os
import webbrowser
import subprocess

# Start the Django server
def start_server():
    # Change the directory to your Django project
    # Always use the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Run the Django server in a subprocess
    subprocess.Popen(['python', 'manage.py', 'runserver'])

    # Open the browser to the specified URL
    webbrowser.open('http://127.0.0.1:8000/')

if __name__ == '__main__':
    start_server()
