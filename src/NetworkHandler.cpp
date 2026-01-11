#include "NetworkHander.h"
#include <opencv2/imgcodecs.hpp>

NetworkHandler::NetworkHandler()  : context(1), publisher(context, ZMQ_PUB){
	// Constructor implementation
}

void NetworkHandler::init(std::string protocol) {
	publisher.bind(protocol);
}

void NetworkHandler::sendFrame(cv::Mat frame) {
	if(frame.empty()) {
		throw std::runtime_error("Empty frame cannot be sent.");
		return;
	}

	std::vector<uchar> buffer;
	std::vector<int> params;
	params.push_back(cv::IMWRITE_JPEG_QUALITY);
	params.push_back(80);
	cv::imencode(".jpeg", frame, buffer, params,);
	zmq::message_t message(buffer.size());

	mcpy(buffer.data(), message.data(), buffer.size());
	publisher.send(message, zmq :: send_flags :: none);

}