#pragma once

#include <opencv2/opencv.hpp>

class CameraHander {

public:
	CameraHander();
	bool openCamera(int cameraIndex);
	cv::Mat captureFrame();

private:
	cv::VideoCapture cap;


};
