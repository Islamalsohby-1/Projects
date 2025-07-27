import pytesseract
import cv2
import numpy as np
from pdf2image import convert_from_path
import layoutparser as lp
from PIL import Image

def preprocess_image(image_path):
    """Preprocess image for better OCR accuracy."""
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray)
    thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return thresh

def extract_text_from_image(image_path, ocr_model='tesseract', focus_region=None):
    """Extract text from an image using specified OCR model."""
    img = preprocess_image(image_path)
    
    if focus_region:
        x, y, w, h = focus_region
        img = img[y:y+h, x:x+w]
    
    if ocr_model == 'pytesseract':
        text = pytesseract.image_to_string(img, lang='eng')
    else:  # Default to tesseract
        text = pytesseract.image_to_string(img, lang='eng')
    
    # Layout analysis
    model = lp.Detectron2LayoutModel(
        config_path='lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config',
        label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"},
        extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8]
    )
    image = lp.image.Image.fromarray(img)
    layout = model.detect(image)
    layout_info = [(block.type, block.text) for block in layout if block.text]
    
    return text, layout_info

def extract_text_from_pdf(pdf_path, ocr_model='tesseract', focus_region=None):
    """Extract text from a PDF by converting to images."""
    images = convert_from_path(pdf_path)
    full_text = []
    layout_info = []
    
    for img in images:
        img_array = np.array(img)
        img_array = preprocess_image(img_array)
        
        if focus_region:
            x, y, w, h = focus_region
            img_array = img_array[y:y+h, x:x+w]
        
        if ocr_model == 'pytesseract':
            text = pytesseract.image_to_string(img_array, lang='eng')
        else:
            text = pytesseract.image_to_string(img_array, lang='eng')
        
        model = lp.Detectron2LayoutModel(
            config_path='lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config',
            label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"},
            extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.8]
        )
        image = lp.image.Image.fromarray(img_array)
        layout = model.detect(image)
        layout_info.extend([(block.type, block.text) for block in layout if block.text])
        
        full_text.append(text)
    
    return '\n'.join(full_text), layout_info