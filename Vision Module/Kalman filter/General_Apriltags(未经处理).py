#Ggeneral_Apriltags - By: 就要吃两碗饭 - 周一 7月 25 2022

import sensor, image, time,utime



f_x = (2.8 / 3.984) * 160 # find_apriltags defaults to this if not set
f_y = (2.8 / 2.952) * 120 # find_apriltags defaults to this if not set
c_x = 160 * 0.5 # find_apriltags defaults to this if not set (the image.w * 0.5)
c_y = 120 * 0.5 # find_apriltags defaults to this if not set (the image.h * 0.5)
K_x  = 23

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)

while(True):
    sensor.skip_frames(time = 0)
    sensor.set_auto_gain(False)
    clock = time.clock()
    clock.tick()
    img = sensor.snapshot()
    find_tag = img.find_apriltags() #找APRILTAG
    if find_tag:
      for tag in img.find_apriltags(fx=f_x, fy=f_y, cx=0, cy=c_y):
       img.draw_rectangle(tag.rect(),color = (255, 0, 0))
       img.draw_cross(tag.cx(), tag.cy(), color = (255, 0, 0))

