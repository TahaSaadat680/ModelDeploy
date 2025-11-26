from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import tensorflow as tf
from tensorflow import keras
from PIL import Image
import io
import base64
import time
import os
import requests
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Enable CORS for React/Next.js frontend

# Configuration
MODEL_PATH = 'best_90plus_model.h5'
CENTROIDS_PATH = 'class_centroids.npy'
IMAGE_SIZE = (299, 299)

# Model download URLs from Google Drive
MODEL_URL = os.environ.get('MODEL_URL', '')
CENTROIDS_URL = os.environ.get('CENTROIDS_URL', '')

# Class names in order
CLASS_NAMES = [
    'alluvial', 'black', 'cinder', 'clay', 
    'laterite', 'peat', 'red', 'sandy', 'yellow'
]

def download_file_from_google_drive(file_id, filepath):
    """Download file from Google Drive using gdown"""
    try:
        import gdown
        print(f"Downloading {filepath} from Google Drive (ID: {file_id})...")
        
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, filepath, quiet=False)
        
        # Check if file was actually downloaded
        if Path(filepath).exists():
            file_size = Path(filepath).stat().st_size
            print(f"{filepath} downloaded successfully! ({file_size / (1024*1024):.1f}MB)")
            return True
        else:
            print(f"Failed to download {filepath}")
            return False
        
    except Exception as e:
        print(f"Error downloading {filepath}: {e}")
        return False

def download_file(url, filepath):
    """Download file from URL (supports Google Drive)"""
    if not url:
        return False
    
    # Check if it's a Google Drive URL
    if 'drive.google.com' in url:
        # Extract file ID from URL
        if '/d/' in url:
            file_id = url.split('/d/')[1].split('/')[0]
        elif 'id=' in url:
            file_id = url.split('id=')[1].split('&')[0]
        else:
            print(f"Could not extract file ID from URL: {url}")
            return False
        
        return download_file_from_google_drive(file_id, filepath)
    
    # Regular download for other URLs
    try:
        print(f"Downloading {filepath}...")
        response = requests.get(url, stream=True, timeout=300)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        print(f"{filepath} downloaded successfully!")
        return True
    except Exception as e:
        print(f"Error downloading {filepath}: {e}")
        return False

def download_models():
    """Download model and centroids if not present"""
    # Download model
    if not Path(MODEL_PATH).exists():
        if MODEL_URL:
            download_file(MODEL_URL, MODEL_PATH)
        else:
            print(f"Warning: {MODEL_PATH} not found and MODEL_URL not set")
    
    # Download centroids
    if not Path(CENTROIDS_PATH).exists():
        if CENTROIDS_URL:
            download_file(CENTROIDS_URL, CENTROIDS_PATH)
        else:
            print(f"Warning: {CENTROIDS_PATH} not found and CENTROIDS_URL not set")

# Download models if needed
download_models()

# Load model and centroids
print("Loading model...")
try:
    model = keras.models.load_model(MODEL_PATH)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    print("Please upload the model file to Railway or set MODEL_URL environment variable")
    model = None

print("Loading class centroids...")
try:
    class_centroids = np.load(CENTROIDS_PATH, allow_pickle=True)
    print(f"Class centroids loaded! Shape: {class_centroids.shape}")
except Exception as e:
    print(f"Error loading centroids: {e}")
    class_centroids = None


def preprocess_image(image):
    """
    Preprocess image for InceptionV3 model
    - Resize to 299x299
    - Apply InceptionV3 preprocessing
    """
    # Resize image
    image = image.resize(IMAGE_SIZE)
    
    # Convert to array
    img_array = np.array(image)
    
    # Ensure RGB (convert RGBA to RGB if needed)
    if img_array.shape[-1] == 4:
        img_array = img_array[:, :, :3]
    
    # Add batch dimension
    img_array = np.expand_dims(img_array, axis=0)
    
    # Apply InceptionV3 preprocessing
    img_array = tf.keras.applications.inception_v3.preprocess_input(img_array)
    
    return img_array


def decode_image_from_request(request_data):
    """
    Decode image from request (supports file upload and base64)
    """
    # Check if file upload
    if 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            raise ValueError("No file selected")
        
        image = Image.open(file.stream)
        return image
    
    # Check if JSON with base64 image
    elif request.is_json:
        data = request.get_json()
        
        if 'image' in data:
            # Handle base64 encoded image
            image_data = data['image']
            
            # Remove data URL prefix if present
            if 'base64,' in image_data:
                image_data = image_data.split('base64,')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            return image
        else:
            raise ValueError("No 'image' field in JSON request")
    
    else:
        raise ValueError("Invalid request format. Use multipart/form-data or JSON with base64 image")


@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "message": "Soil Classification API",
        "model": "InceptionV3",
        "classes": len(CLASS_NAMES),
        "model_loaded": model is not None,
        "endpoints": {
            "health": "/health",
            "predict": "/predict (POST)",
            "classes": "/classes",
            "model_info": "/model-info"
        }
    })


@app.route('/health')
def health():
    return jsonify({
        "status": "healthy" if model is not None else "model_not_loaded",
        "model_loaded": model is not None,
        "centroids_loaded": class_centroids is not None,
        "num_classes": len(CLASS_NAMES),
        "message": "Upload model file or set MODEL_URL environment variable" if model is None else "Ready"
    }), 200


@app.route('/classes')
def get_classes():
    return jsonify({
        "classes": CLASS_NAMES,
        "count": len(CLASS_NAMES)
    })


@app.route('/model-info')
def model_info():
    return jsonify({
        "model_type": "InceptionV3 (Transfer Learning)",
        "input_shape": [299, 299, 3],
        "num_classes": len(CLASS_NAMES),
        "classes": CLASS_NAMES,
        "preprocessing": "InceptionV3 preprocessing function",
        "model_loaded": model is not None
    })


@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({
            "success": False,
            "error": "Model not loaded. Please upload the model file to Railway."
        }), 503
    
    start_time = time.time()
    
    try:
        # Decode image from request
        image = decode_image_from_request(request)
        
        # Preprocess image
        processed_image = preprocess_image(image)
        
        # Make prediction
        predictions = model.predict(processed_image, verbose=0)
        
        # Get predicted class
        predicted_index = int(np.argmax(predictions[0]))
        predicted_class = CLASS_NAMES[predicted_index]
        confidence = float(predictions[0][predicted_index])
        
        # Create probabilities dictionary
        probabilities = {
            CLASS_NAMES[i]: float(predictions[0][i])
            for i in range(len(CLASS_NAMES))
        }
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        return jsonify({
            "success": True,
            "prediction": {
                "class": predicted_class,
                "class_index": predicted_index,
                "confidence": confidence,
                "probabilities": probabilities
            },
            "processing_time": round(processing_time, 3)
        })
    
    except ValueError as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 400
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
