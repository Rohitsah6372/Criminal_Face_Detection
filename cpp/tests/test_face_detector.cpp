// test_face_detector.cpp
// Sample test for the FaceDetector interface
#include "mylib/face_detector.h"
#include <gtest/gtest.h>
#include <opencv2/core.hpp>

TEST(FaceDetectorTest, DetectsNoFacesInBlankImage) {
  auto detector = mylib::CreateDefaultFaceDetector();
  cv::Mat blank = cv::Mat::zeros(100, 100, CV_8UC1);
  auto faces = detector->Detect(blank);
  EXPECT_TRUE(faces.empty());
} 