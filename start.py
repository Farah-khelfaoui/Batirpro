import os
import subprocess
import sys
import time

def start_backend():
    print("Starting Backend (Django)...")
    os.chdir('BatiPro')
    # Activate the virtual environment and run the Django server in a new terminal window
    subprocess.run(['start', 'cmd', '/K', '.\\env\\Scripts\\activate.bat && python manage.py runserver'], shell=True)

def start_frontend():
    print("Starting Frontend (React)...")
    os.chdir('..')  # Go back to the parent directory (where FrontBatirpro is)
    os.chdir('FrontBatirpro') 
    # Run React in a new terminal window
    subprocess.run(['start', 'cmd', '/K', 'npm start'], shell=True)

def main():
    try:
        # Start Backend in a new terminal window
        start_backend()
        
        # Adding a small delay before starting the Frontend
        time.sleep(2)
        
        # Start Frontend in a new terminal window
        start_frontend()

    except KeyboardInterrupt:
        print("Project startup was interrupted.")
        sys.exit()

if __name__ == '__main__':
    main()