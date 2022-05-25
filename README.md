# Adaptive Traffic Control

This project is represented by two programs. 

## Vehicle detector
<p>The first is program is a vehicle detector based on the YOLOv3-320 architecture. This algorithm allows detecting cars, motorbikes, trucks, buses and bicycles, as well as pedestrians on the video stream. Data on the number of vehicles and pedestrians is regularly written to a file, which can be used as input for the adaptive traffic control algorithm (from one direction of the intersection). To test the detector, run <a href="https://github.com/nickimpark/Adaptive-Traffic-Control/blob/main/vehicle_detector/detector.py">detector.py</a>. Don't forget to download the files to initialize YOLOv3-320 model: <a href="https://github.com/pjreddie/darknet/blob/master/cfg/yolov3.cfg">yolov3.cfg</a> and <a href="https://pjreddie.com/media/files/yolov3.weights">yolov3.weights</a>. These files must be in the same directory as the algorithm.</p>

![image](https://user-images.githubusercontent.com/48395531/170374915-220c85a4-9bda-4ff8-bee7-0ae952ba84e8.png)


## Adaptive traffic control algorithm
<p>The second program allows you to test the adaptive traffic control algorithm in the traffic simulator (check this <a href="https://github.com/BilHim/trafficSimulator">project</a> from <a href="https://github.com/BilHim">BilHim</a>). You can familiarize yourself with my adaptive algorithm by opening <a href="https://github.com/nickimpark/Adaptive-Traffic-Control/blob/main/traffic_control/trafficSimulator/traffic_signal.py">traffic_signal.py</a>. Traffic data is assumed to come from 4 directions of the intersection. You can test the algorithm by running <a href="https://github.com/nickimpark/Adaptive-Traffic-Control/blob/main/traffic_control/intersection.py">intersection.py</a>. It allows you to increase the number of cars passing the intersection in 10 minutes by 29% with an uneven distribution of traffic.</p>

![image](https://user-images.githubusercontent.com/48395531/170375000-e66f82fb-cd54-4b7a-b233-b8b4a3bee336.png)
