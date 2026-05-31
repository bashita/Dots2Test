# Dots2Test
Dots2Text is a camera based assistive technology web application built to detect real physical embossed Braille dots from photographs or live camera feed and converts them into English text with text to speech output.

# How does it work?
When a user uploads a photo or captures a webcam frame, the image goes through a processing pipeline. First, OpenCV converts it to grayscale and applies adaptive thresholding to handle different lighting conditions. Then contour detection finds all the raised dots on the paper by checking their size and circularity. Once the dots are found, the app estimates the spacing between them to figure out where each Braille cell starts and ends. Each cell is a 2-column by 3-row grid of 6 possible dot positions. The detected dot positions are mapped to standard Braille dot numbers (1 through 6), which are then looked up in the Grade 1 Braille dictionary to produce the final English letter or character.
