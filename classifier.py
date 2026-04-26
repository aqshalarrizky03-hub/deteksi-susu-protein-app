import cv2
import pytesseract
import re
from PIL import Image

keywords = {
    "whey": ["whey", "whey isolate", "whey concentrate", "whey protein"],
    "casein": ["casein", "micellar casein", "calcium caseinate"],
    "plant": ["soy protein", "pea protein", "rice protein", "vegan", "plant protein"],
    "mass_gainer": ["mass gainer", "weight gainer", "maltodextrin", "carbohydrate", "high calorie"]
}

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return text

def classify_protein(text):
    text = preprocess_text(text)
    score = {k:0 for k in keywords}

    for category, words in keywords.items():
        for word in words:
            if word in text:
                score[category] += 1

    if score["mass_gainer"] > 0:
        score["mass_gainer"] += 2

    result = max(score, key=score.get)
    return result, score

def process_image(pil_img):
    import numpy as np
    import cv2
    import pytesseract

    # convert ke numpy
    img = np.array(pil_img)

    # RGB → BGR
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # preprocessing
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    median = cv2.medianBlur(gray, 3)
    thresh = cv2.threshold(median, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    text = pytesseract.image_to_string(thresh)
    kategori, score = classify_protein(text)

   total_score = sum(score.values())
   return text, kategori, total_score, gray, thresh
