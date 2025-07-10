#!/usr/bin/env python3
"""
Script to add RTMP camera feed to the employee attendance system
"""

import requests
import sys

def add_rtmp_camera():
    """Add the RTMP camera feed to the system"""
    
    # Camera feed details
    camera_data = {
        'name': 'Test RTMP Stream',
        'camera_type': 'rtsp',  # Using rtsp type for RTMP streams
        'camera_url': 'rtmp://13.203.184.235/live/stream/test',
        'location': 'Remote Server',
        'description': 'RTMP stream from remote server for testing'
    }
    
    try:
        # Make the API call to add camera feed
        response = requests.post('http://localhost:5000/add_camera_feed', data=camera_data)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("✅ RTMP camera feed added successfully!")
                print(f"Camera Name: {camera_data['name']}")
                print(f"Camera URL: {camera_data['camera_url']}")
                print(f"Camera Type: {camera_data['camera_type']}")
                print(f"Location: {camera_data['location']}")
                print("\nYou can now:")
                print("1. Go to Camera Feeds page to see the new camera")
                print("2. Test the connection using the Test button")
                print("3. Start detection using the Start Detection button")
                return True
            else:
                print(f"❌ Error adding camera: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the Flask application.")
        print("Make sure the Flask app is running on http://localhost:5000")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_camera_connection():
    """Test if the camera feed is working"""
    try:
        # First, get the camera feeds to find the ID
        response = requests.get('http://localhost:5000/camera_feeds')
        if response.status_code == 200:
            camera_feeds = response.json()
            # Find our RTMP camera
            rtmp_camera = None
            for camera in camera_feeds:
                if camera['camera_url'] == 'rtmp://13.203.184.235/live/stream/test':
                    rtmp_camera = camera
                    break
            
            if rtmp_camera:
                print(f"✅ Found RTMP camera with ID: {rtmp_camera['id']}")
                
                # Test the camera connection
                test_response = requests.get(f"http://localhost:5000/test_camera_feed/{rtmp_camera['id']}")
                if test_response.status_code == 200:
                    test_result = test_response.json()
                    if test_result.get('status') == 'success':
                        print("✅ Camera connection test successful!")
                        return True
                    else:
                        print(f"❌ Camera connection test failed: {test_result.get('message', 'Unknown error')}")
                        return False
                else:
                    print(f"❌ Error testing camera: HTTP {test_response.status_code}")
                    return False
            else:
                print("❌ RTMP camera not found in the system")
                return False
        else:
            print(f"❌ Error getting camera feeds: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing camera: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Adding RTMP Camera Feed to Employee Attendance System")
    print("=" * 60)
    
    # Check if requests module is available
    try:
        import requests
    except ImportError:
        print("❌ Error: 'requests' module not found.")
        print("Please install it using: pip install requests")
        sys.exit(1)
    
    # Add the camera feed
    print("\n📹 Adding RTMP camera feed...")
    if add_rtmp_camera():
        print("\n🧪 Testing camera connection...")
        test_camera_connection()
        
        print("\n🎯 Next Steps:")
        print("1. Open your browser and go to: http://localhost:5000")
        print("2. Navigate to 'Camera Feeds' in the menu")
        print("3. Find 'Test RTMP Stream' in the list")
        print("4. Click the 'Start Detection' button (eye icon)")
        print("5. The system will start detecting faces from your RTMP stream")
        
        print("\n📋 Camera Details:")
        print("• Name: Test RTMP Stream")
        print("• URL: rtmp://13.203.184.235/live/stream/test")
        print("• Type: RTSP Stream (for RTMP processing)")
        print("• Location: Remote Server")
    else:
        print("\n❌ Failed to add RTMP camera feed.")
        print("Please check that:")
        print("1. The Flask application is running")
        print("2. The application is accessible at http://localhost:5000")
        print("3. The RTMP server is accessible") 