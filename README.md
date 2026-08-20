# WebbFinder

WebbFinder is a desktop application that lets you explore the images and scientific information from the James Webb Space Telescope through the official ESA/Webb image API.

## Overview

The app retrieves image metadata from the ESA/Webb API and displays the image along with its title, description, link, and date. The images can be browsed in chronological order or searched by date, and can be downloaded in different resolutions.

## Features

- Browse the archive of all the available James Webb space telescope images
- Jump to a certain date by entering a date in the format of (YYYY-MM-DD) to find the image closest to that date
- View each image's title, date, description, and link to its official ESA/Webb page
- Download the images in medium, large, or original resolutions
- Utilization of threads to fetch data and preload neighbouring images without blocking the main interface
- After initial download, image metadata is stored in data.json, making the future lauches significantly faster

<img width="701" height="671" alt="image" src="https://github.com/user-attachments/assets/1fc24d4e-bcbd-4f00-92dd-0a5797a2f634" />

## Installation

1. Clone the repository:
  ```bash
  git clone [https://github.com/cream-of-wheat/WebbFinder.git](https://github.com/cream-of-wheat/WebbFinder.git)
  cd WebbFinder
  ```
2. Install the required dependencies:
  ```bash
  pip install -r requirements.txt
  ```
   (Note: The download dialog uses tkinter. This comes pre-installed with python on windows, but if you are on mac or linux, you might need to install it through your package manager)

3. Run the application:
  ```bash
  python main.py
  ```
   (Note: On the first launch, the app will build a local `data.json` cache of the image library, which may take a few moments. Subsequent launches will be much faster. If you wish to skip this, download the data.json file in the repository. Or enjoy the simple animation :D)

## Usage
* Navigation: Click the '<' and '>' buttons or use the left/right arrow keys to cycle through the images
* Read more: Click the blue hyperlink to open the official ESA/Webb page in your default web browser for more information
* Select your preferred resolution from the dropdown menu in the bottom right and click to save it to your local drive

## Acknowledgements
* Imagery and data provided by the official [NASA/ESA/CSA James Webb Space Telescope API](https://esawebb.org/).
