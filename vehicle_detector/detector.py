import numpy as np
import cv2  # Build OpenCV with CUDA available first (using CMake)
from collections import Counter


class VehicleDetector:
    def __init__(self):
        self.confThreshold = 0.5  # Confidence threshold
        self.nmsThreshold = 0.4  # Non-maximum suppression threshold
        # 320x320, 416x416 or 608x608 input image in YOLOv3
        self.inpWidth = 320  # Width of input image (to model)
        self.inpHeight = 320  # Height of input image (to model)
        # Classes names
        self.classesFile = 'coco.names'
        self.classes = None
        self.colors = None
        self.white_list = None
        # Initialize the model, load these files for YOLOv3-320 from: https://pjreddie.com/darknet/yolo/
        self.modelConfiguration = 'yolov3.cfg'
        self.modelWeights = 'yolov3.weights'
        self.net = cv2.dnn.readNetFromDarknet(self.modelConfiguration, self.modelWeights)
        # Use CUDA
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        self.video_source = 0  # 0 is your standard camera, can be changed to your stream link (commented example below)
        # self.video_source = 'http://raspberrypi.local:8000/stream.mjpg'  # 10 FPS, 640x480
        self.N_frames = 10  # for writing traffic data to file every 10 frames of video

    def load_classes(self):
        with open(self.classesFile, 'rt') as f:
            self.classes = f.read().rstrip('\n').split('\n')
        # Define random colour for each class
        np.random.seed(42)
        self.colors = np.random.randint(0, 255, size=(len(self.classes), 3), dtype='uint8')
        # We need only this classes
        self.white_list = ['person', 'bicycle', 'car', 'motorbike', 'bus', 'truck']

    # Get names of the output layers (layers with unconnected outputs)
    def get_outputs_names(self):
        layers_names = self.net.getLayerNames()
        return [layers_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]

    def postprocess(self, frame, outs):
        frame_height = frame.shape[0]
        frame_width = frame.shape[1]
        class_ids = []
        confidences = []
        boxes = []
        detected_names = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > self.confThreshold:
                    center_x = int(detection[0] * frame_width)
                    center_y = int(detection[1] * frame_height)
                    width = int(detection[2] * frame_width)
                    height = int(detection[3] * frame_height)
                    left = int(center_x - width / 2)
                    top = int(center_y - height / 2)
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
                    boxes.append([left, top, width, height])

        # Non-max suppression
        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.confThreshold, self.nmsThreshold)
        # Draw and append final detections
        for i in indices:
            i = i[0]  # comment this line if not using CUDA
            box = boxes[i]
            left = box[0]
            top = box[1]
            width = box[2]
            height = box[3]
            self.draw_pred(frame, class_ids[i], confidences[i], left, top, left + width, top + height)
            detected_names.append(self.classes[class_ids[i]])

        frequency = Counter(detected_names)

        # Draw text
        cv2.putText(frame, 'Person:     ' + str(frequency['person']), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0, 255, 0), 2)
        cv2.putText(frame, 'Bicycle:     ' + str(frequency['bicycle']), (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0, 255, 0), 2)
        cv2.putText(frame, 'Car:        ' + str(frequency['car']), (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0, 255, 0), 2)
        cv2.putText(frame, 'Motorbike:  ' + str(frequency['motorbike']), (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0, 255, 0), 2)
        cv2.putText(frame, 'Bus:        ' + str(frequency['bus']), (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0, 255, 0), 2)
        cv2.putText(frame, 'Truck:      ' + str(frequency['truck']), (20, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0, 255, 0), 2)

        return frequency

    def draw_pred(self, frame, class_id, conf, left, top, right, bottom):
        # Only for classes in white list!
        if self.classes[class_id] not in self.white_list:
            return
        # Bounding box
        color = (int(self.colors[int(class_id)][0]), int(self.colors[int(class_id)][1]), int(self.colors[int(class_id)][2]))
        cv2.rectangle(frame, (left, top), (right, bottom), color, 1)

        label = '{} {:.2f}'.format(self.classes[class_id], conf)
        # Label at the top of bounding box
        text_size, _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        text_w, text_h = text_size
        cv2.rectangle(frame, (left, top), (left + text_w, top - text_h),
                      color, cv2.FILLED)
        cv2.putText(frame, label,
                    (left, top), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    def operate(self):
        cap = cv2.VideoCapture(self.video_source)
        self.N_frames = 10 # for writing traffic data to file every 10 frames of video
        cnt = 0  # frame counter (for writing traffic data every N_frames frames)
        # press Q or Esc to stop
        while cv2.waitKey(1) < 0:
            hasFrame, frame = cap.read()
            if not hasFrame:
                cv2.waitKey(3000)
                # Release device
                cap.release()
                break

            blob = cv2.dnn.blobFromImage(frame, 1 / 255, (self.inpWidth, self.inpHeight), [0, 0, 0], 1, crop=False)
            self.net.setInput(blob)
            outs = self.net.forward(self.get_outputs_names())
            frequency = self.postprocess(frame, outs)
            cv2.imshow('detection', frame)

            # Record traffic data every N frames
            cnt += 1
            if cnt == self.N_frames:
                with open('video_detection.txt', 'w') as fout:
                    fout.write(
                        'Person;Bicycle;Car;Motorbike;Bus;Truck\n{};{};{};{};{};{}\n'.format(frequency['person'],
                                                                                             frequency['bicycle'],
                                                                                             frequency['car'],
                                                                                             frequency['motorbike'],
                                                                                             frequency['bus'],
                                                                                             frequency['truck']))

                cnt = 0


if __name__ == '__main__':
    detector = VehicleDetector()
    detector.load_classes()
    detector.operate()
