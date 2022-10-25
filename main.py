import cv2
import numpy as np
# import urllib
# import urllib.request
import json
import boto3
from datetime import datetime

s3 = boto3.client('s3')
# req = urllib.request.urlopen('https://leafareainfo.s3.ap-south-1.amazonaws.com/image.jpg')
# arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
# img = cv2.imdecode(arr, -1)

def lambda_handler(event, context):
    bucket_name = event["pathParameters"]["bucket"]
    file_name = event["queryStringParameters"]["file"]
    fileobj = s3.get_objects(Bucket=bucket_name, Key=file_name)
    nparr = np.frombuffer(fileobj['Body'].read(), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    resizeimg = cv2.resize(img, (400,400))
    resizeimg_copy = resizeimg.copy()
    hsv = cv2.cvtColor(resizeimg, cv2.COLOR_BGR2HSV)

    # Black Mask
    # upper_black = np.array([360,255,50])
    lower_black = np.array([0,0,0])
    upper_black = np.array([360,255,100])
    mask_black = cv2.inRange(hsv, lower_black, upper_black)

    contours, _ = cv2.findContours(mask_black, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    sorted_contours = sorted(contours, key=cv2.contourArea, reverse=True)

    for i, cont in enumerate(sorted_contours[:1],1):
        x = cv2.drawContours(resizeimg, cont, -1, (0,255,0), 3)
        cv2.putText(resizeimg, str(i), (cont[0,0,0],cont[0,0,1]-10), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0,255,0), 4)
    dt = str(datetime.now())
    name_black = "Black-contour.jpg : " + dt 
    cv2.imwrite(name_black, x)
    s3.upload_file(name_black,'leafareainfo',name_black)

    def find_contour_areas(contours):
        areas = []
        for cnt in contours:
            cont_area = cv2.contourArea(cnt)
            areas.append(cont_area)
        return areas

    sorted_contours_by_area = sorted(contours, key=cv2.contourArea, reverse=True)
    frame_area = find_contour_areas(sorted_contours_by_area)[0]

    # Green Mask

    lower_green = np.array([36, 25, 25])
    upper_green = np.array([86, 255, 255])
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    contoursG, _ = cv2.findContours(mask_green, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    sorted_contoursG = sorted(contoursG, key=cv2.contourArea, reverse=True)

    for i, cont in enumerate(sorted_contoursG[:1],1):
        x = cv2.drawContours(resizeimg_copy, cont, -1, (0,255,0), 3)
        cv2.putText(resizeimg_copy, str(i), (cont[0,0,0],cont[0,0,1]-10), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0,255,0), 4)
    dtg = str(datetime.now())
    name_green = "Green-Contour.jpg : " + dtg
    cv2.imwrite(name_green, x)
    s3.upload_file(name_green,'leafareainfo',name_green)

    def find_contour_areas(contoursG):
        areas = []
        for cnt in contoursG:
            cont_area = cv2.contourArea(cnt)
            areas.append(cont_area)
        return areas

    sorted_contours_by_area = sorted(contoursG, key=cv2.contourArea, reverse=True)
    leaf_area = find_contour_areas(sorted_contours_by_area)[0]

    # Calculation

    total_area_BG = frame_area+leaf_area
    ratio = total_area_BG/leaf_area

    actual_frame_area = 8250

    actual_leaf_area = actual_frame_area/ratio


    value = {
    "frame-area" : actual_frame_area,
    "leaf-area" : actual_leaf_area 
    }

    return json.dumps(value)

    







