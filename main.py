import Hand_tracking_module as htm
import cv2 as cv
import time
import numpy as np
import random
import os
#pygame to play sound effects
import pygame
#this function lists the images in the folder and returns a list of images
#this function takes the folder path and the list of image names as input and returns a list of images
def listProvider(folderPath,myList):
    list1=[]
    for imPath in myList:
        image = cv.imread(f'{folderPath}\{imPath}')
        list1.append(image)
    return list1

#this function changes the heart image to black when the player loses a life
#this function takes the number of lives left and the list of heart images as input and returns the updated list
def lives_left(num,list1):
    list1[num]= cv.imread(r"C:\Users\OMEN\Desktop\Skills\Prashy Projects\Fruit Ninja\Player_hearts\black.jpg")
    return list1

# this function displays the heart images on the screen
# it takes the image and the list of heart images as input and returns the image with hearts
def heart_shower(img,lives_list):
    distance=20
    for live in lives_list:
        y_coord,x_coord= live.shape[0:2]
        img[0:y_coord, distance:distance+x_coord] = live
        distance= distance + x_coord
    return img

# this function provides the image data for the fruit
# it takes the image number and the list of images as input and returns the image data
def image_data_provider(num,list1):
    global wCam
    height,width =overlayList_image[image_number].shape[0:2]
    x_variable = random.randint(0,wCam - width)
    return [image_number, x_variable, width, height,50]
#basic setup
wCam, hCam = 700,700
cap = cv.VideoCapture(0)
detector=htm.handDetector(detectionCon=0.9)
pTime=0

# Gets the fruits images in the folder
image_folderPath = r"C:\Users\OMEN\Desktop\Skills\Prashy Projects\Fruit Ninja\Fruit_Images"
myList_image = os.listdir(image_folderPath)
overlayList_image = listProvider(image_folderPath,myList_image).copy()

# Initialize variables
# image_counter is used to control the frequency of fruit generation
image_counter=0
total_score=0

# Speed controllers for the fruits
# These control how fast the fruits fall and move horizontally
speed_controller_vertical=3
speed_controller_horizontal=1

#Game related variables
level_number=0
total_life=3
extra_point=0
#stores corrdinate of the last 5 frames of the index finger's top point
#this is used to draw a line that follows the finger
coordinate_list = []
fruit_status_list=[]
while True:
    #conditions for different levels
    if total_score <10:
        level_number=1
        speed_controller_vertical=3
        speed_controller_horizontal=1
    elif total_score < 20:
        level_number=2
        speed_controller_vertical=6
        speed_controller_horizontal=2
    elif total_score < 30:
        level_number=3
        speed_controller_vertical=9
        speed_controller_horizontal=3
    elif total_score < 40:
        level_number=4
        speed_controller_vertical=12
        speed_controller_horizontal=4
    elif total_score < 100:
        level_number=5
        speed_controller_vertical=15
        speed_controller_horizontal=5
    else:
        level_number=6
        speed_controller_vertical=20
        speed_controller_horizontal=6

    # Randomly select an image number for the fruit
    # This number corresponds to the index of the fruit in the overlayList_image
    image_number=random.randint(0, len(overlayList_image)-1)

    #stores coordinate of index finger's top point
    lmList=[]
    success, img = cap.read()
    img = detector.findHands(img)
    img=cv.resize(img,(hCam,wCam))
    
    if total_life==3:
        lives_list= [cv.imread(r"C:\Users\OMEN\Desktop\Skills\Prashy Projects\Fruit Ninja\Player_hearts\red.jpg")]
        lives_list.append(lives_list[0])
        lives_list.append(lives_list[0])
    #draws the heart images on the screen
    img= heart_shower(img,lives_list)

    # Makes a copy of the original image to restore it later
    original_img = img.copy()

    if detector.findPosition(img,draw=False):
        #Makes the follow up line 
        lmList = detector.findPosition(img, draw=True)
        if image_counter<5:
            coordinate_list.append(lmList[0][1:3])
            #print("counted")
        else:
            coordinate_list.pop(0)
            coordinate_list.append(lmList[0][1:3])
        
        if len(coordinate_list) == 5:
            for i in range(4):
                cv.line(img, (coordinate_list[i][0], coordinate_list[i][1]),(coordinate_list[i+1][0], coordinate_list[i+1][1]), (170, 170, 170),5)
        
        
        
        image_counter+=1
    # If the list of landmarks is not empty, extract the coordinates of the index finger's tip
    # This is used to determine where the player is slicing the fruit
    if len(lmList) > 0:
        new_lm_list= lmList.copy()
        new_lm_list= new_lm_list[0][1:3]

    # If the image counter is a multiple of 30, generate a new fruit
    # This controls how often new fruits appear on the screen
    if image_counter%30==1:
        fruit_status_list.append((image_data_provider(image_number,overlayList_image)))
    
    # Update the position of each fruit in the fruit_status_list
    # Move the fruit downwards and horizontally based on the speed controllers
    for fruit in fruit_status_list:
        img[fruit[4]:fruit[4]+fruit[3], fruit[1]:fruit[1]+fruit[2]] = original_img[fruit[4]:fruit[4]+fruit[3], fruit[1]:fruit[1]+fruit[2]]
        fruit[4]+= speed_controller_vertical  # Move the fruit downwards
        fruit[1]+=speed_controller_horizontal  # Move the fruit horizontally
        
        # Check if the fruit has gone off the screen
        # If it has, remove it from the list and update the score/lives accordingly
        if fruit[4] + fruit[3]> hCam:
            extra_point=-2
            fruit_status_list.remove(fruit)
            if fruit[0] == 2:
                extra_point=0
            total_score+= extra_point
            
        # Check if the fruit has gone off the right side of the screen
        # If it has, reset its position to the left side of the screen
        if fruit[1] + fruit[2] > wCam:
            fruit[1]=0
    # Draw the fruit on the screen    
    for fruit in fruit_status_list:
        
        img[fruit[4]:fruit[4]+fruit[3], fruit[1]:fruit[1]+fruit[2]] = overlayList_image[fruit[0]]
        #if index finger's tip is close to the fruit, slice it
        if len(new_lm_list) > 0 and np.linalg.norm(np.array([new_lm_list[0], new_lm_list[1]]) - np.array([fruit[1]+fruit[2]/2, fruit[4]+fruit[3]/2])) < 50 :
            fruit_status_list.remove(fruit)
            img[fruit[4]:fruit[4]+fruit[3], fruit[1]:fruit[1]+fruit[2]] = original_img[fruit[4]:fruit[4]+fruit[3], fruit[1]:fruit[1]+fruit[2]]
            # Check which fruit was sliced and update score/lives accordingly
            if fruit[0] == 0:
                pygame.mixer.init()
                pygame.mixer.music.load(r'C:\Users\OMEN\Desktop\Skills\Prashy Projects\Fruit Ninja\Sounds\sword.mp3')
                pygame.mixer.music.play()
                #print("Apple sliced!")
                extra_point = 1
                total_score += 1
            elif fruit[0] == 1:
                #print("Banana sliced!")
                pygame.mixer.init()
                pygame.mixer.music.load(r'C:\Users\OMEN\Desktop\Skills\Prashy Projects\Fruit Ninja\Sounds\sword.mp3')
                pygame.mixer.music.play()
                extra_point = 2
                total_score += 2
            elif fruit[0] == 3:
                #print("Coconut sliced!")
                pygame.mixer.init()
                pygame.mixer.music.load(r'C:\Users\OMEN\Desktop\Skills\Prashy Projects\Fruit Ninja\Sounds\sword.mp3')
                pygame.mixer.music.play()
                extra_point = 3
                total_score += 3
            else:
                #print("It was a bomb! You lose 1 life")
                total_life -= 1
                lives_list=lives_left(total_life,lives_list)
                img= heart_shower(img,lives_list)
                pygame.mixer.init()
                pygame.mixer.music.load(r'C:\Users\OMEN\Desktop\Skills\Prashy Projects\Fruit Ninja\Sounds\bomb.mp3')
                pygame.mixer.music.play()
                if total_life <= 0:
                    #print("Game Over! You have no lives left.")
                    cv.putText(img, "Game Over!", (wCam//2 - 100, hCam//2), cv.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 3)
                    cv.destroyAllWindows()
                    exit()
    
    if extra_point > 0:
        cv.putText(img, f'+{extra_point}', (200,150), cv.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3)
    elif extra_point < 0:
        cv.putText(img, f'{extra_point}', (200,150), cv.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
    # FPS Counter
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv.putText(img, f'Level: {level_number}', (40, 100), cv.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
    cv.putText(img, f'Score: {total_score}', (40, 150), cv.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
    cv.imshow("Img",img)
    cv.waitKey(1)