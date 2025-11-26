# 🌱 Soil Classification API

A production-ready Flask API that uses InceptionV3 deep learning model to classify 9 types of soil from images. Deployed on Railway with Git LFS for efficient model storage.

## 📊 Model Details

- **Architecture**: InceptionV3 (Transfer Learning)
- **Input Size**: 299×299 RGB images
- **Accuracy**: ~92% validation accuracy
- **Classes**: 9 soil types
  ```
  alluvial, black, cinder, clay, laterite, peat, red, sandy, yellow
  ```

## 🚀 Live Deployment

**GitHub Repository**: [TahaSaadat680/ModelDeploy](https://github.com/TahaSaadat680/ModelDeploy)

**Deployment**: Railway (with Git LFS for 220MB model)

## 📡 API Endpoints

### `GET /`
Health check with API information.

**Response:**
```json
{
  "status": "online",
  "message": "Soil Classification API",
  "model": "InceptionV3",
  "classes": 9,
  "model_loaded": true
}
```

### `GET /health`
Detailed health status.

### `GET /classes`
Get list of all soil types.

### `POST /predict`
**Main prediction endpoint** - Upload an image and get soil type prediction.

**Request (Multipart Form):**
```bash
curl -X POST https://your-app.railway.app/predict \
  -F "file=@soil_image.jpg"
```

**Request (JSON with Base64):**
```bash
curl -X POST https://your-app.railway.app/predict \
  -H "Content-Type: application/json" \
  -d '{"image": "data:image/jpeg;base64,/9j/4AAQ..."}'
```

**Response:**
```json
{
  "success": true,
  "prediction": {
    "class": "black",
    "class_index": 1,
    "confidence": 0.9234,
    "probabilities": {
      "alluvial": 0.0123,
      "black": 0.9234,
      "cinder": 0.0156,
      "clay": 0.0089,
      "laterite": 0.0145,
      "peat": 0.0098,
      "red": 0.0067,
      "sandy": 0.0034,
      "yellow": 0.0054
    }
  },
  "processing_time": 0.234
}
```

## 💻 Frontend Integration

### React/Next.js Example

```javascript
async function classifySoil(imageFile) {
  const formData = new FormData();
  formData.append('file', imageFile);

  const response = await fetch('https://your-app.railway.app/predict', {
    method: 'POST',
    body: formData
  });

  const result = await response.json();

  if (result.success) {
    console.log('Soil Type:', result.prediction.class);
    console.log('Confidence:', (result.prediction.confidence * 100).toFixed(2) + '%');
    return result;
  } else {
    console.error('Error:', result.error);
  }
}

// Usage in component
<input
  type="file"
  accept="image/*"
  onChange={(e) => classifySoil(e.target.files[0])}
/>
```

### Complete React Component

```jsx
import { useState } from 'react';

export default function SoilClassifier() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('https://your-app.railway.app/predict', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input type="file" accept="image/*" onChange={handleUpload} />

      {loading && <p>Analyzing soil...</p>}

      {result?.success && (
        <div>
          <h3>Soil Type: {result.prediction.class}</h3>
          <p>Confidence: {(result.prediction.confidence * 100).toFixed(2)}%</p>
        </div>
      )}
    </div>
  );
}
```

## 🛠️ Local Development

### Prerequisites
- Python 3.10+
- Git with Git LFS installed

### Setup

```bash
# Clone repository
git clone https://github.com/TahaSaadat680/ModelDeploy.git
cd ModelDeploy

# Install Git LFS and pull model files
git lfs install
git lfs pull

# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py
```

The API will be available at `http://localhost:5000`

### Test Locally

```bash
# Health check
curl http://localhost:5000/health

# Predict
curl -X POST http://localhost:5000/predict \
  -F "file=@test_image.jpg"
```

## 🚢 Deployment to Railway

### Step 1: Push to GitHub

```bash
# Make sure Git LFS is installed
git lfs install

# Push to GitHub
git push origin main
```

**Note**: Model files (220MB) are handled by Git LFS automatically.

### Step 2: Deploy on Railway

1. Go to [railway.app](https://railway.app)
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your repository: `TahaSaadat680/ModelDeploy`
4. Railway automatically:
   - Detects Python project
   - Installs dependencies from `requirements.txt`
   - Pulls Git LFS files (model + centroids)
   - Starts app using `Procfile`
5. Generate a public domain in Railway settings
6. Your API is live! 🎉

### Expected Deployment Time
- Build: 3-5 minutes
- First request: 10-15 seconds (cold start)
- Subsequent requests: 200-500ms

## 📂 Project Structure

```
ModelDeploy/
├── app.py                    # Flask API server
├── best_90plus_model.h5      # InceptionV3 model (220MB, via LFS)
├── class_centroids.npy       # Class centroids (via LFS)
├── requirements.txt          # Python dependencies
├── Procfile                  # Railway start command
├── runtime.txt               # Python version (3.10.12)
├── .gitattributes            # Git LFS configuration
├── .gitignore                # Git ignore rules
└── .railwayignore            # Railway ignore rules
```

## ⚙️ Configuration

### Environment Variables (Optional)

Set these in Railway if you want to host model files externally:

- `MODEL_URL` - Direct download URL for model file
- `CENTROIDS_URL` - Direct download URL for centroids file

The app will download these on startup if the files aren't present locally.

### CORS

CORS is enabled for all origins by default. To restrict, modify `app.py:15`:

```python
CORS(app, origins=["https://your-frontend.com"])
```

## 📋 Requirements

```
flask==3.0.0
flask-cors==4.0.0
tensorflow==2.15.0
numpy==1.24.3
Pillow==10.1.0
gunicorn==21.2.0
requests==2.31.0
gdown==4.7.1
```

## 🎯 Image Requirements

- **Formats**: JPG, JPEG, PNG
- **Size**: Recommended < 10MB
- **Resolution**: Any (automatically resized to 299×299)
- **Color**: RGB (RGBA converted automatically)

## ⚡ Performance

- **Cold Start**: 10-15 seconds (first request after idle)
- **Inference Time**: 200-500ms per prediction
- **Model Size**: 220MB (loaded into memory)
- **Concurrent Requests**: Supported

## 🐛 Error Handling

All errors return JSON with appropriate HTTP status codes:

**400 Bad Request:**
```json
{
  "success": false,
  "error": "No file selected"
}
```

**503 Service Unavailable:**
```json
{
  "success": false,
  "error": "Model not loaded"
}
```

## 🔍 Troubleshooting

### Model not loading
- Check Railway logs for errors
- Verify Git LFS pulled files: `git lfs ls-files`
- Confirm file size: `best_90plus_model.h5` should be ~220MB

### Slow predictions
- First request is always slower (cold start)
- Consider Railway Pro plan for always-on instances

### CORS errors
- CORS is enabled by default
- Check Railway URL is correct in frontend
- Verify request format (multipart/form-data or JSON)

## 📊 Model Training Details

- **Dataset**: 15,136 soil images (9 classes)
- **Training**: InceptionV3 with transfer learning
- **Fine-tuning**: Last 150 layers unfrozen
- **Validation Accuracy**: 92.26%
- **Preprocessing**: InceptionV3 preprocessing + augmentation

## 📄 License

MIT License - feel free to use for your projects!

## 👨‍💻 Author

**Taha Saadat**
- GitHub: [@TahaSaadat680](https://github.com/TahaSaadat680)
- Repository: [ModelDeploy](https://github.com/TahaSaadat680/ModelDeploy)

## 🙏 Acknowledgments

- Model trained using InceptionV3 architecture
- Deployed on Railway with Git LFS
- Built with Flask, TensorFlow, and Python

---

**Status**: ✅ Production Ready | 🚀 Deployed on Railway | 📦 Git LFS Enabled

For questions or issues, please open an issue on [GitHub](https://github.com/TahaSaadat680/ModelDeploy/issues).
