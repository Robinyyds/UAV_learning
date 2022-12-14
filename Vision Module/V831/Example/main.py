# generated by maixhub, tested on maixpy3 v0.4.8
from maix import nn, camera, display, image
import serial

input_size = (224, 224)
model = "model-111.awnn.mud"
labels = ['circle', 'circle_blue', 'rectangle', 'rectangle_blue', 'start', 'triangle', 'triangle_blue']
anchors = [3.78, 3.78, 1.78, 1.78, 4.97, 4.97, 0.97, 0.97, 2.72, 2.72]

class YOLOv2:
    def __init__(self, model_path, labels, anchors, net_in_size, net_out_size):
        self.labels = labels
        self.anchors = anchors
        self.net_in_size = net_in_size
        self.net_out_size = net_out_size
        print("-- load model:", model)
        self.model = nn.load(model_path)
        print("-- load ok")
        print("-- init yolo2 decoder")
        self._decoder = nn.decoder.Yolo2(len(labels), anchors, net_in_size=net_in_size, net_out_size=net_out_size)
        print("-- init complete")

    def run(self, img, nms=0.3, threshold=0.5):
        out = self.model.forward(img, layout="hwc")
        boxes, probs = self._decoder.run(out, nms=nms, threshold=threshold, img_size=input_size)
        return boxes, probs

    def draw(self, img, boxes, probs):
        ser = serial.Serial("/dev/ttyS1",115200)

        for i, box in enumerate(boxes):
            x=0
            y=0
            xing=0
            color=0
            class_id = probs[i][0]
            prob = probs[i][1][class_id]
            msg = "{}:{:.2f}%".format(self.labels[class_id], prob*100)
            mmm = "x={xx},y={yy}".format(xx=(box[0]+box[2]/2)-112,yy= -((box[1]+box[3]/2)-112))
            img.draw_rectangle(box[0], box[1], box[0] + box[2], box[1] + box[3], color=(255, 255, 255), thickness=2)
            img.draw_string(box[0] + 2, box[1] + 2, msg, scale = 1.2, color = (255, 255, 255), thickness = 2)
            img.draw_string(112,112,msg,scale = 1.2, color = (255, 255, 255), thickness = 2)
            if (self.labels[class_id]=='rectangle'):
                xing=1
                color=1
            elif (self.labels[class_id]=='rectangle_blue'):
                xing=1
                color=2
            elif (self.labels[class_id]=='circle'):
                xing=2
                color=1
            elif (self.labels[class_id]=='circle_blue'):
                xing=2
                color=2
            elif (self.labels[class_id]=='triangle'):
                xing=3
                color=1
            elif (self.labels[class_id]=='triangle_blue'):
                xing=3
                color=2
            x = (box[0]+box[2]/2)-112
            y = -((box[1]+box[3]/2)-112)
            if x > 0 and y > 0:
                check=0
            elif x > 0 and y < 0:
                check=1
            elif x < 0 and y > 0:
                check=2
            elif x < 0 and y < 0:
                check=3
            ser.write(bytearray([0xaa,0x41,xing,color,x,y,check,0x00]))


def main():
    camera.config(size=input_size)
    yolov2 = YOLOv2(model, labels, anchors, input_size, (input_size[0] // 32, input_size[1] // 32))
    while True:
        img = camera.capture()
        boxes, probs = yolov2.run(img, nms=0.3, threshold=0.5)
        yolov2.draw(img, boxes, probs)
        display.show(img)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback, time
        msg = traceback.format_exc()
        print(msg)
        img = image.new(size = (240, 240), color = (255, 0, 0), mode = "RGB")
        img.draw_string(0, 0, msg, scale = 0.8, color = (255, 255, 255), thickness = 1)
        display.show(img)
        time.sleep(20)
