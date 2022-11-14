# Downtime Analyzer Script
![analyzer_screenshot_sample](https://user-images.githubusercontent.com/32603299/201578724-ca0445c4-f32d-4e1d-8ea4-2cd745f421d3.PNG)
# Introduction
Downtime Data Analyzer is a simple Python script that performs calculations on ".csv" file that contains downtime recodrs from database. We plot graphs with matplotlib embedded in Tk. The data is gathered in another aplication - kiosk screen that runs Power Apps with Dataverse.
- This is a personal project for simple OEE calculations ( downtime, availability)
- The main purpose of this project is to learn basics of Python, pandas, matplotlib & Tk 

# Dependencies
- matplotlib >= 3.5.3
- pytz >= 2022.2
- tkcalendar >= 1.6.1
## Package as standalone executable
Install PyInstaller from PyPI:

>pip install pyinstaller

Go to your program’s directory and run:

>pyinstaller launcher.py --splash splashfile.png --debug bootloader --hidden-import "babel.numbers" --icon=small_icon.ico
