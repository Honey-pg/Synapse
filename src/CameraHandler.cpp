#include "CameraHandler.hpp"

// Constructor
CameraHandler::CameraHandler() {
  
}

bool CameraHandler::initCamera(int id) {
    return cap.open(id); // Ab ye 'cap' ko pehchan lega
}

cv::Mat CameraHandler::getFrame() {
    cv::Mat tempFrame;
    cap >> tempFrame;
    if (tempFrame.empty())
        return tempFrame;
	cv::flip(tempFrame, tempFrame, 1);
    /*input and output dono same hai jisse 
    in - place operation hota hai, new memory allocate nahi hoti 
    */
    return tempFrame;
}