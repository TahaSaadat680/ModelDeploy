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

app = Flask(__name__)
CORS(app)  # Enable CORS for React/Next.js frontend

# Configuration
MODEL_PATH = 'best_90plus_model.h5'
IMAGE_SIZE = (299, 299)

# Class names in order
CLASS_NAMES = [
    'alluvial', 'black', 'cinder', 'clay',
    'laterite', 'peat', 'red', 'sandy', 'yellow'
]

# Load model
print("Loading model...")
try:
    model = keras.models.load_model(MODEL_PATH)
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None


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
        "num_classes": len(CLASS_NAMES),
        "message": "Ready" if model is not None else "Model not loaded"
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
            "error": "Model not loaded. Please check server logs."
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
