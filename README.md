# Soil Classification API

Deploy an InceptionV3-based soil classification model that accepts image uploads and returns predictions for 9 soil types.

## Model Details

- **Architecture**: InceptionV3 (Transfer Learning)
- **Input**: 299x299 RGB images
- **Classes**: 9 soil types
  - alluvial, black, cinder, clay, laterite, peat, red, sandy, yellow
- **Preprocessing**: InceptionV3 preprocessing function

## API Endpoints

### GET /

Health check endpoint with API information.

**Response:**
```json
{
  "status": "online",
  "message": "Soil Classification API",
  "model": "InceptionV3",
  "classes": 9,
  "endpoints": { ... }
}
```

### GET /health

Detailed health status.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "centroids_loaded": true,
  "num_classes": 9
}
```

### GET /classes

Get list of soil classes.

**Response:**
```json
{
  "classes": ["alluvial", "black", "cinder", ...],
  "count": 9
}
```

### GET /model-info

Get model metadata.

### POST /predict

Main prediction endpoint. Accepts image upload and returns soil type prediction.

**Request (File Upload):**
```bash
curl -X POST http://localhost:5000/predict \
  -F "file=@soil_sample.jpg"
```

**Request (Base64 JSON):**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
  }'
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
      ...
    }
  },
  "processing_time": 0.234
}
```

### POST /predict-with-centroids

Alternative prediction using centroid-based classification.

## Frontend Integration (React/Next.js)

### File Upload Example

```javascript
async function classifySoil(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  try {
    const response = await fetch('https://your-app.railway.app/predict', {
      method: 'POST',
      body: formData
    });
    
    const result = await response.json();
    
    if (result.success) {
      console.log('Predicted soil type:', result.prediction.class);
      console.log('Confidence:', result.prediction.confidence);
      return result;
    } else {
      console.error('Prediction failed:', result.error);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}

// Usage in component
const handleFileUpload = async (event) => {
  const file = event.target.files[0];
  if (file) {
    const result = await classifySoil(file);
    // Update UI with result
  }
};
```

### Base64 Upload Example

```javascript
async function classifySoilBase64(imageDataUrl) {
  try {
    const response = await fetch('https://your-app.railway.app/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        image: imageDataUrl
      })
    });
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('Error:', error);
  }
}
```

### Complete React Component Example

```jsx
import { useState } from 'react';

export default function SoilClassifier() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState(null);

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Show preview
    setPreview(URL.createObjectURL(file));
    setLoading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('https://your-app.railway.app/predict', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input 
        type="file" 
        accept="image/*" 
        onChange={handleImageUpload}
      />
      
      {preview && (
        <img src={preview} alt="Preview" style={{maxWidth: '300px'}} />
      )}
      
      {loading && <p>Analyzing soil...</p>}
      
      {result && result.success && (
        <div>
          <h3>Results:</h3>
          <p>Soil Type: <strong>{result.prediction.class}</strong></p>
          <p>Confidence: {(result.prediction.confidence * 100).toFixed(2)}%</p>
          
          <h4>All Probabilities:</h4>
          <ul>
            {Object.entries(result.prediction.probabilities).map(([soil, prob]) => (
              <li key={soil}>
                {soil}: {(prob * 100).toFixed(2)}%
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
```

## Local Development

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Locally

```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Test with cURL

```bash
# Health check
curl http://localhost:5000/health

# Get classes
curl http://localhost:5000/classes

# Predict (with image file)
curl -X POST http://localhost:5000/predict \
  -F "file=@path/to/soil_image.jpg"
```

## Deployment to Railway

### 1. Prepare Repository

```bash
# Initialize git
git init

# Add files
git add .

# Commit
git commit -m "Initial commit: Soil classification API"
```

### 2. Create GitHub Repository

1. Go to [GitHub](https://github.com/new)
2. Create a new repository (e.g., `soil-classification-api`)
3. Don't initialize with README (we already have files)

### 3. Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/soil-classification-api.git
git branch -M main
git push -u origin main
```

### 4. Deploy on Railway

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your `soil-classification-api` repository
6. Railway will automatically:
   - Detect Python
   - Install dependencies from `requirements.txt`
   - Use `Procfile` to start the app
7. Wait for deployment (5-10 minutes for first deploy)

### 5. Get Your URL

1. Click on your project in Railway
2. Go to "Settings" → "Domains"
3. Click "Generate Domain"
4. Your API will be available at: `https://your-app.railway.app`

### 6. Test Deployment

```bash
# Test health endpoint
curl https://your-app.railway.app/health

# Test prediction
curl -X POST https://your-app.railway.app/predict \
  -F "file=@test_image.jpg"
```

## Image Requirements

- **Formats**: JPG, JPEG, PNG
- **Size**: Recommended < 10MB
- **Resolution**: Any (will be resized to 299x299)
- **Color**: RGB (RGBA will be converted)

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad request (invalid image, missing file, etc.)
- `500`: Internal server error

**Error Response:**
```json
{
  "success": false,
  "error": "Error message here"
}
```

## Performance Notes

- **First Request**: May take 5-10 seconds (cold start, model loading)
- **Subsequent Requests**: ~0.2-0.5 seconds
- **Model Size**: 221MB (loaded into memory)
- **Concurrent Requests**: Supported (limited by Railway plan)

## Environment Variables

Railway automatically sets:
- `PORT`: Application port (don't hardcode)

Optional variables you can set:
- `FLASK_ENV`: Set to `production` for production deployment

## Monitoring

Railway provides built-in monitoring:
- View logs in real-time
- Check CPU/Memory usage
- Monitor request metrics

## Troubleshooting

### Deployment Fails

- Check Railway build logs
- Ensure all files are committed to Git
- Verify `requirements.txt` is correct

### Model Not Loading

- Check that `best_90plus_model.h5` is in repository
- Verify file size < 500MB (Railway limit)
- Check Railway logs for error messages

### Slow Predictions

- First request is always slower (cold start)
- Consider Railway Pro plan for better performance
- Implement caching if needed

### CORS Issues

- CORS is enabled by default in `app.py`
- If issues persist, check browser console
- Verify frontend URL is correct

## License

Add your license information here.

## Contact

Add your contact information here.
