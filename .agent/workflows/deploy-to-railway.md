---
description: Deploy model to Railway
---

# Deploy Soil Classification Model to Railway

Complete guide to deploy your InceptionV3-based soil classification model to Railway.

## Prerequisites

1. Railway account at https://railway.app/
2. GitHub account
3. Git installed on your machine
4. Python 3.10+ installed locally (for testing)

## Quick Start (Local Testing)

Before deploying, test the API locally:

### 1. Install Dependencies

```bash
cd f:\Model
pip install -r requirements.txt
```

### 2. Run the API

```bash
python app.py
```

The API will start at `http://localhost:5000`

### 3. Test the API

In a new terminal:

```bash
# Test health endpoint
curl http://localhost:5000/health

# Test with an image (replace with your test image path)
curl -X POST http://localhost:5000/predict -F "file=@path/to/soil_image.jpg"
```

Or use the test script:

```bash
python test_api.py
```

## Deployment to Railway

### Step 1: Initialize Git Repository

```bash
cd f:\Model
git init
git add .
git commit -m "Initial commit: Soil classification API"
```

### Step 2: Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository (e.g., `soil-classification-api`)
3. **Important**: Do NOT initialize with README, .gitignore, or license

### Step 3: Push to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/soil-classification-api.git
git branch -M main
git push -u origin main
```

### Step 4: Deploy on Railway

1. Go to https://railway.app/
2. Click "Login" and sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Authorize Railway to access your GitHub
6. Select your `soil-classification-api` repository
7. Railway will automatically:
   - Detect it's a Python project
   - Install dependencies from `requirements.txt`
   - Use the `Procfile` to start the app
   - Assign a port automatically

### Step 5: Wait for Deployment

- First deployment takes 5-10 minutes (large model file)
- Watch the build logs in Railway dashboard
- Look for "Build successful" and "Deployment live"

### Step 6: Get Your API URL

1. In Railway dashboard, click on your project
2. Go to "Settings" tab
3. Scroll to "Domains" section
4. Click "Generate Domain"
5. Your API URL will be: `https://your-app-name.railway.app`

### Step 7: Test Deployed API

```bash
# Replace with your Railway URL
export API_URL="https://your-app-name.railway.app"

# Test health
curl $API_URL/health

# Test prediction
curl -X POST $API_URL/predict -F "file=@test_image.jpg"
```

## Frontend Integration

### React/Next.js Example

```javascript
// components/SoilClassifier.jsx
import { useState } from 'react';

export default function SoilClassifier() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

  const handleUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_URL}/predict`, {
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
      <input type="file" accept="image/*" onChange={handleUpload} />
      {loading && <p>Analyzing...</p>}
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

### Environment Variables

Add to your `.env.local`:

```
NEXT_PUBLIC_API_URL=https://your-app-name.railway.app
```

## Troubleshooting

### Build Fails on Railway

**Issue**: "Failed to install dependencies"

**Solution**:
- Check Railway build logs
- Ensure `requirements.txt` is correct
- Verify Python version in `runtime.txt`

### Model File Too Large

**Issue**: "File size exceeds limit"

**Solution**:
- Railway free tier supports up to 500MB
- Your model is 221MB, should be fine
- If issues persist, upgrade to Pro plan

### Slow First Request

**Issue**: First API call takes 10+ seconds

**Solution**:
- This is normal (cold start + model loading)
- Subsequent requests will be fast (~0.2-0.5s)
- Consider Railway Pro for always-on instances

### CORS Errors

**Issue**: "CORS policy blocked"

**Solution**:
- CORS is already enabled in `app.py`
- Check browser console for exact error
- Verify API URL is correct in frontend

### Prediction Errors

**Issue**: "Invalid image format"

**Solution**:
- Ensure image is JPG, JPEG, or PNG
- Check file size (< 10MB recommended)
- Verify image is not corrupted

## API Endpoints Reference

### GET /health
Check API status

### GET /classes
Get list of soil types

### GET /model-info
Get model metadata

### POST /predict
Main prediction endpoint

**Request**: Multipart form-data with `file` field
**Response**: JSON with prediction and probabilities

## Performance Tips

1. **Image Size**: Resize images client-side before upload
2. **Caching**: Implement caching for repeated predictions
3. **Batch Processing**: Process multiple images in parallel
4. **Monitoring**: Use Railway metrics to track performance

## Cost Considerations

**Railway Free Tier**:
- $5 credit per month
- Enough for ~500-1000 predictions/month
- Sleeps after inactivity

**Railway Pro**:
- $20/month
- Always-on instances
- Better performance
- More resources

## Next Steps

1. ✅ Test API locally
2. ✅ Deploy to Railway
3. ⬜ Integrate with frontend
4. ⬜ Add authentication (if needed)
5. ⬜ Set up monitoring
6. ⬜ Add rate limiting (for production)

## Support

For issues:
- Check Railway documentation: https://docs.railway.app
- Review build logs in Railway dashboard
- Test locally first to isolate issues

## Model Information

- **Training Accuracy**: ~72% (from notebook)
- **Validation Accuracy**: ~72%
- **Classes**: 9 soil types
- **Architecture**: InceptionV3 transfer learning
- **Input Size**: 299x299 RGB
