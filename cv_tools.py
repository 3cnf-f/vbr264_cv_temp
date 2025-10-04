import os
import numpy as np
import cv2
from google.api_core.client_options import ClientOptions
from google.cloud import vision
import json

def detect_text_with_confidence(path, api_key):
    """Detects text in the image file and returns words with confidence scores.
    reads from written files not from cv2. takes file path and returns annotations as well as a cv2 image where bounding boxes have been added"""

    client_options = ClientOptions(api_key=api_key)
    client = vision.ImageAnnotatorClient(client_options=client_options)
    
    with open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    cv2_img=cv2.imread(path)

    # Use document_text_detection for more detailed results including confidence
    response = client.document_text_detection(image=image)
    
    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    # The first text annotation is the full text of the image.
    # Subsequent annotations are for individual words.
    # To get confidence for each word, we need to iterate through the fullTextAnnotation
    
    all_word_data = []
    poly_gone_away =[]

    # The response from document_text_detection contains a fullTextAnnotation
    # which is structured into pages, blocks, paragraphs, words, and symbols.
    for page in response.full_text_annotation.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    word_text = ''.join([
                        symbol.text for symbol in word.symbols
                    ])
                    confidence = word.confidence
                    vertices = [(vertex.x, vertex.y)
                                for vertex in word.bounding_box.vertices]
                    
                    word_data = {
                        "word": word_text,
                        "confidence": confidence,
                        "bounding_box": vertices
                    }
                    all_word_data.append(word_data)
                    # Convert vertices to numpy array of integers for OpenCV
                    # Each point is [x, y], reshaped to (-1, 1, 2) for polylines
                    pts = np.array([[vertex[0], vertex[1]] for vertex in vertices], np.int32)
                    pts = pts.reshape((-1, 1, 2))
                    
                    # Draw the polygon outline on the image
                    # True for closed shape, (0,255,0) for green color, 1 for thickness
                    cv2.polylines(cv2_img, [pts], True, (0, 255, 0), 1)
                    # poly_gone_away=poly_gone_away.reshape((-1,1,2))
                    # Calculate position for text "hello" above the top of the bounding box
                    min_x = min(vertex[0] for vertex in vertices)
                    min_y = min(vertex[1] for vertex in vertices)
                    text_pos = (int(min_x), int(min_y - 5))  # 5 pixels above the top edge
                    
                    # Draw the text "hello" above the polygon
                    # Using HERSHEY_SIMPLEX font, scale 0.5, blue color (255,0,0), thickness 1
                    cv2.putText(cv2_img,word_text, text_pos, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)



    return all_word_data,cv2_img

