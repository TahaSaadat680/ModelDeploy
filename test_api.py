"""
Test script for the Soil Classification API
Run this after starting the Flask app to verify everything works
"""

import requests
import base64
from pathlib import Path

# API base URL (change this when deployed to Railway)
BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_classes():
    """Test classes endpoint"""
    print("\n=== Testing Classes Endpoint ===")
    response = requests.get(f"{BASE_URL}/classes")
    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Number of classes: {data['count']}")
    print(f"Classes: {data['classes']}")
    return response.status_code == 200

def test_model_info():
    """Test model info endpoint"""
    print("\n=== Testing Model Info Endpoint ===")
    response = requests.get(f"{BASE_URL}/model-info")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200

def test_predict_with_file(image_path):
    """Test prediction with file upload"""
    print(f"\n=== Testing Prediction with File Upload ===")
    print(f"Image: {image_path}")
    
    if not Path(image_path).exists():
        print(f"Error: Image file not found: {image_path}")
        return False
    
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/predict", files=files)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            pred = data['prediction']
            print(f"✓ Predicted Class: {pred['class']}")
            print(f"✓ Confidence: {pred['confidence']:.4f}")
            print(f"✓ Processing Time: {data['processing_time']}s")
            print(f"\nTop 3 Predictions:")
            sorted_probs = sorted(pred['probabilities'].items(), 
                                 key=lambda x: x[1], reverse=True)
            for soil, prob in sorted_probs[:3]:
                print(f"  {soil}: {prob:.4f}")
            return True
        else:
            print(f"Error: {data['error']}")
            return False
    else:
        print(f"Error: {response.text}")
        return False

def test_predict_with_base64(image_path):
    """Test prediction with base64 encoded image"""
    print(f"\n=== Testing Prediction with Base64 ===")
    print(f"Image: {image_path}")
    
    if not Path(image_path).exists():
        print(f"Error: Image file not found: {image_path}")
        return False
    
    # Read and encode image
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Create data URL
    image_data_url = f"data:image/jpeg;base64,{image_data}"
    
    # Send request
    response = requests.post(
        f"{BASE_URL}/predict",
        json={'image': image_data_url},
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data['success']:
            pred = data['prediction']
            print(f"✓ Predicted Class: {pred['class']}")
            print(f"✓ Confidence: {pred['confidence']:.4f}")
            return True
        else:
            print(f"Error: {data['error']}")
            return False
    else:
        print(f"Error: {response.text}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Soil Classification API - Test Suite")
    print("=" * 60)
    
    # Test basic endpoints
    results = []
    results.append(("Health Check", test_health()))
    results.append(("Classes", test_classes()))
    results.append(("Model Info", test_model_info()))
    
    # Test prediction endpoints
    # You need to provide a test image path
    test_image = "test_soil_image.jpg"  # Change this to your test image
    
    if Path(test_image).exists():
        results.append(("Predict (File Upload)", test_predict_with_file(test_image)))
        results.append(("Predict (Base64)", test_predict_with_base64(test_image)))
    else:
        print(f"\n⚠ Warning: Test image not found: {test_image}")
        print("Please provide a test image to test prediction endpoints")
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:30} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! API is ready for deployment.")
    else:
        print("\n⚠ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API")
        print("Make sure the Flask app is running:")
        print("  python app.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
