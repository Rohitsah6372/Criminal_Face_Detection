// face_detector.h
// Interface for a face detector module
#ifndef MYLIB_FACE_DETECTOR_H_
#define MYLIB_FACE_DETECTOR_H_

#include <vector>
#include <string>
#include <opencv2/core.hpp>

namespace mylib {

// Abstract interface for face detection
class FaceDetector {
 public:
  virtual ~FaceDetector() = default;

  // Detect faces in the given image. Returns bounding boxes.
  virtual std::vector<cv::Rect> Detect(const cv::Mat& image) const = 0;
};

// Factory function to create a default face detector
std::unique_ptr<FaceDetector> CreateDefaultFaceDetector();

}  // namespace mylib

#endif  // MYLIB_FACE_DETECTOR_H_ 