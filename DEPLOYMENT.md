# Deployment Guide

## Repository Status ✅

The repository has been cleaned and is ready for deployment to Railway!

### What was done:
1. ✅ Removed the 220MB model from Git history (was causing push failures)
2. ✅ Set up Git LFS to handle large model files efficiently
3. ✅ Repository size reduced from 220MB+ to ~423KB
4. ✅ Model (`best_90plus_model.h5`) and centroids (`class_centroids.npy`) are tracked with Git LFS
5. ✅ Updated configurations for Railway deployment
6. ✅ API returns proper JSON responses for frontend integration

## Push to GitHub

Now you can push to GitHub without issues:

```bash
# If pushing to a new remote:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main

# If remote already exists:
git push origin main --force
```

**Note:** The `--force` flag is needed because we rewrote the Git history to remove the large model files.

## Deploy to Railway

### Option 1: Deploy from GitHub (Recommended)

1. Go to [Railway](https://railway.app/)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Railway will automatically detect:
   - `Procfile` for the start command
   - `requirements.txt` for Python dependencies
   - `runtime.txt` for Python version (3.10.12)
5. Railway will pull the LFS files automatically during build
6. Your app will be live! 🚀

### Option 2: Deploy Directly to Railway

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy
railway up
```

## API Endpoints

Once deployed, your API will have these endpoints:

- `GET /` - API status and info
- `GET /health` - Health check
- `GET /classes` - List of soil types
- `GET /model-info` - Model information
- `POST /predict` - Predict soil type from image

## Testing the API

### Using cURL:
```bash
curl -X POST https://your-app.railway.app/predict \
  -F "file=@soil_image.jpg"
```

### Using JavaScript (Frontend):
```javascript
const formData = new FormData();
formData.append('file', imageFile);

const response = await fetch('https://your-app.railway.app/predict', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(result);
// {
//   "success": true,
//   "prediction": {
//     "class": "sandy",
//     "class_index": 7,
//     "confidence": 0.95,
//     "probabilities": { ... }
//   },
//   "processing_time": 0.123
// }
```

## Important Notes

- ⚠️ Make sure Git LFS is installed when cloning: `git lfs install && git lfs pull`
- ⚠️ Railway automatically handles LFS during deployment
- ⚠️ The model will be loaded on Railway startup (may take 10-15 seconds on first request)
- ⚠️ CORS is enabled for all origins (configure in `app.py` if needed)

## Environment Variables (Optional)

If you want to host the model elsewhere (Google Drive, S3, etc.), you can set these in Railway:

- `MODEL_URL` - Direct download URL for the model file
- `CENTROIDS_URL` - Direct download URL for the centroids file

The app will automatically download these files on startup if they're not present.

## Troubleshooting

### If Railway build fails:
1. Check Railway logs for specific error messages
2. Verify all dependencies are in `requirements.txt`
3. Ensure Python version in `runtime.txt` is supported by Railway

### If model doesn't load:
1. Check that Git LFS pulled the files correctly: `git lfs ls-files`
2. Verify file sizes: `best_90plus_model.h5` should be ~220MB
3. Check Railway logs for model loading errors

## Files Included

- `app.py` - Flask API server
- `requirements.txt` - Python dependencies
- `Procfile` - Railway start command
- `runtime.txt` - Python version
- `best_90plus_model.h5` - Trained InceptionV3 model (via LFS)
- `class_centroids.npy` - Class centroids for predictions (via LFS)
- `.gitattributes` - Git LFS configuration
- `.railwayignore` - Files to exclude from Railway deployment

## Next Steps

1. Push to GitHub: `git push origin main --force`
2. Deploy to Railway from your GitHub repository
3. Test the API endpoints
4. Integrate with your frontend application

Good luck with your deployment! 🚀
