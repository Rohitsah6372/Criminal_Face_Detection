// face_detector.cpp
// Implementation of the FaceDetector interface
#include "mylib/face_detector.h"
#include <opencv2/objdetect.hpp>
#include <memory>

namespace mylib {

class HaarCascadeFaceDetector : public FaceDetector {
 public:
  HaarCascadeFaceDetector() {
    // Load OpenCV's default face cascade
    cascade_.load("haarcascade_frontalface_default.xml");
  }

  std::vector<cv::Rect> Detect(const cv::Mat& image) const override {
    std::vector<cv::Rect> faces;
    cascade_.detectMultiScale(image, faces, 1.1, 3, 0, cv::Size(30, 30));
    return faces;
  }

 private:
  cv::CascadeClassifier cascade_;
};

std::unique_ptr<FaceDetector> CreateDefaultFaceDetector() {
  return std::make_unique<HaarCascadeFaceDetector>();
}

}  // namespace mylib 