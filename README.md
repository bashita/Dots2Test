# Dots2Test
Dots2Text is a camera based assistive technology web application built to detect real physical embossed Braille dots from photographs or live camera feed and converts them into English text with text to speech output.

# How does it work?
When a user uploads a photo or captures a webcam frame, the image goes through a processing pipeline. First, OpenCV converts it to grayscale and applies adaptive thresholding to handle different lighting conditions. Then contour detection finds all the raised dots on the paper by checking their size and circularity. Once the dots are found, the app estimates the spacing between them to figure out where each Braille cell starts and ends. Each cell is a 2-column by 3-row grid of 6 possible dot positions. The detected dot positions are mapped to standard Braille dot numbers (1 through 6), which are then looked up in the Grade 1 Braille dictionary to produce the final English letter or character.

# What are the files in the project?
The project has five files. app.py is the Flask server that handles image uploads from the browser and serves the web page. processor.py contains the entire OpenCV pipeline that processes images and detects Braille dots. braille_map.py holds the complete Grade 1 Braille mapping — every letter a to z, numbers 0 to 9, and common punctuation. requirements.txt lists the Python libraries needed to run the project. Inside the templates folder, index.html is the full web interface with upload support, live webcam, auto-scan mode, and a speak button.

# Technologies Used
The backend is built with Python and Flask. Image processing is handled by OpenCV and NumPy. Braille recognition uses a custom dot clustering algorithm with a Grade 1 Braille lookup table. Text-to-speech is powered by gTTS (Google Text-to-Speech) with a browser SpeechSynthesis fallback. The frontend is plain HTML, CSS, and JavaScript. The webcam is accessed through the browser's WebRTC MediaDevices API.

# Features
- Detects real physical embossed Braille dots from uploaded images or live webcam
- Adaptive thresholding to handle different lighting conditions
- Circularity filtering for accurate dot isolation from background noise
- Automatic cell size estimation based on dot spacing
- Live webcam scanning with manual capture button
- Auto-scan mode that processes a new frame every 3 seconds
- Text-to-speech output using gTTS with browser fallback
- Smart guidance messages like "too dark", "move closer", "adjust angle"
- Stats panel showing dot count, cell count, and character count

# Team Members
1. Bashita
   Role: Backend Developer and Data collector
2. Lalitha Shree D
   Role: Backend Developer and Tester
3. Kavinaya P
   Role: Frontend Developer and UI Designer
