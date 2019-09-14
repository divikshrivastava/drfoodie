import cv2
import argparse
import numpy as np
import xlrd

ap = argparse.ArgumentParser()
ap.add_argument('-i', '--image', required=True,help = 'path to input image')
ap.add_argument('-c', '--config', required=True,help = 'path to yolo config file')
ap.add_argument('-w', '--weights', required=True,help = 'path to yolo pre-trained weights')
ap.add_argument('-cl', '--classes', required=True,help = 'path to text file containing class names')
args = ap.parse_args()

results=[]
def get_output_layers(net):
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    return output_layers


def draw_prediction(img, class_id, confidence, x, y, x_plus_w, y_plus_h):
    label = str(classes[class_id])
    results.append(label)
    color = COLORS[class_id]
    cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)
    cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

curw=int(input("Enter your current weight"))
tarw=int(input("Enter your target weight"))
days=int(input("Enter the number of days in which you want to achieve the target weight"))
image = cv2.imread(args.image)
Width = image.shape[1]
Height = image.shape[0]
scale = 0.00392
classes = None
with open(args.classes, 'r') as f:
    classes = [line.strip() for line in f.readlines()]

COLORS = np.random.uniform(0, 255, size=(len(classes), 3))
net = cv2.dnn.readNet(args.weights, args.config)
blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=False)
net.setInput(blob)
outs = net.forward(get_output_layers(net))
class_ids = []
confidences = []
boxes = []
conf_threshold = 0.5
nms_threshold = 0.4


for out in outs:
    for detection in out:
        scores = detection[5:]
        class_id = np.argmax(scores)
        confidence = scores[class_id]
        if confidence > 0.5:
            center_x = int(detection[0] * Width)
            center_y = int(detection[1] * Height)
            w = int(detection[2] * Width)
            h = int(detection[3] * Height)
            x = center_x - w / 2
            y = center_y - h / 2
            class_ids.append(class_id)
            confidences.append(float(confidence))
            boxes.append([x, y, w, h])


indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

for i in indices:
    i = i[0]
    box = boxes[i]
    x = box[0]
    y = box[1]
    w = box[2]
    h = box[3]
    draw_prediction(image, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h))

loc='C:\\Users\\HP\\Documents\\GitHub\\DrFoodie\\food calories.xlsx'
#location of the file containing values of calories of different food items
wb = xlrd.open_workbook(loc) 
sheet = wb.sheet_by_index(0)
dictionary = {
  "default": 0
}
for i in range(sheet.nrows): 
    dictionary[sheet.cell_value(i, 0)]=sheet.cell_value(i,1)
totalcal=0
for i in range(0,len(results)):
    ter=str(results[i])
    ter2=str(dictionary[results[i]])
    print("100 gram servings of "+ter+" has "+ter2+" calories.")
    totalcal=totalcal+dictionary[results[i]]
ppp=str(totalcal)    
print("total calories of your meal is "+ppp)
calt=(tarw-curw)*1000
calt=calt/days
if calt<=0:
    calt=calt*-1
    ter=str(calt)
    print("You should consume "+ter+" calories lesser everyday to get to your desired weight")
else:
    ter=str(calt)
    print("You should consume almost "+ter+" calories everyday to get to your desired weight")
    
cv2.imshow("object detection", image)
cv2.waitKey()
    
cv2.imwrite("object-detection.jpg", image)
cv2.destroyAllWindows()
