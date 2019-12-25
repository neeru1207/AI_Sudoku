'''This class takes an input paramater modeltype. If the modeltype is CNN then initialization of
and prediction by the CNN are carried out else the KNN algorithm. This class also preprocesses the grid cell
by blackfilling the outer layers and centering the bounding box of the number'''
import numpy as np
import cv2
import tensorflow as tf
import os
import pickle

class DigitRecognizer:

    '''This function initializes a CNN/KNN based on the input parameter modeltype'''
    def __init__(self, modeltype):
        self.writeimg = True
        self.modeltype = modeltype
        if modeltype == "CNN":
            try:
                self.model = tf.keras.models.load_model("cnn.hdf5")
            except:
                raise Exception("cnn.hdf5 not found!")
        elif modeltype == "KNN":
            try:
                self.model = pickle.load(open("knn.sav", 'rb'))
            except:
                raise Exception("knn.sav not found!")

    '''This function takes a preprocessed image and
    returns the prediction made on the image by the CNN or KNN based on the modeltype'''
    def make_prediction(self, imgpath):
        try:
            cleanedimg = cv2.imread(imgpath, 0)
        except:
            raise Exception("Invalid Image path!")
        if self.modeltype == "CNN":
            lis = [cleanedimg]
            lis = np.reshape(lis, (1, 28, 28, 1))
            idx = None
            pred = self.model.predict(lis)
            for i in range(len(pred[0])):
                if pred[0][i] > 0:
                    idx = i
                    break
            return idx
        elif self.modeltype == "KNN":
            cleanedimg = cleanedimg.reshape(1, -1)
            prediction = self.model.predict(cleanedimg)[0]
            return prediction

    '''This function takes the cell image as input, cleans the image, fills holes,
    finds the bounding box containing the digit, centers the bounding box and returns a vector
    of size 1600 (as the size of each cell is 40X40)'''
    def preprocess_image(self, img):
        rows = np.shape(img)[0]

        #First we need to remove the outermost white pixels.
        #This can be achieved by flood filling with some of the outer points as seeds.
        #After looking at the cell images, I concluded that it's enough if we
        #Flood fill with all the points from the three outermost layers as seeds
        for i in range(rows):
            #Floodfilling the outermost layer
            cv2.floodFill(img, None, (0, i), 0)
            cv2.floodFill(img, None, (i, 0), 0)
            cv2.floodFill(img, None, (rows-1, i), 0)
            cv2.floodFill(img, None, (i, rows-1), 0)
            #Floodfilling the second outermost layer
            cv2.floodFill(img, None, (1, i), 1)
            cv2.floodFill(img, None, (i, 1), 1)
            cv2.floodFill(img, None, (rows - 2, i), 1)
            cv2.floodFill(img, None, (i, rows - 2), 1)
        if self.writeimg:
            try:
                os.remove("StagesImages/14.jpg")
            except:
                pass
            cv2.imwrite("StagesImages/14.jpg", img)
        #Finding the bounding box of the number in the cell
        rowtop = None
        rowbottom = None
        colleft = None
        colright = None
        thresholdBottom = 50
        thresholdTop = 50
        thresholdLeft = 50
        thresholdRight = 50
        center = rows // 2
        for i in range(center, rows):
            if rowbottom is None:
                temp = img[i]
                if sum(temp) < thresholdBottom or i == rows-1:
                    rowbottom = i
            if rowtop is None:
                temp = img[rows-i-1]
                if sum(temp) < thresholdTop or i == rows-1:
                    rowtop = rows-i-1
            if colright is None:
                temp = img[:, i]
                if sum(temp) < thresholdRight or i == rows-1:
                    colright = i
            if colleft is None:
                temp = img[:, rows-i-1]
                if sum(temp) < thresholdLeft or i == rows-1:
                    colleft = rows-i-1

        # Centering the bounding box's contents
        newimg = np.zeros(np.shape(img))
        startatX = (rows + colleft - colright)//2
        startatY = (rows - rowbottom + rowtop)//2
        for y in range(startatY, (rows + rowbottom - rowtop)//2):
            for x in range(startatX, (rows - colleft + colright)//2):
                newimg[y, x] = img[rowtop + y - startatY, colleft + x - startatX]

        if self.writeimg:
            try:
                os.remove("StagesImages/15.jpg")
            except:
                pass
            cv2.imwrite("StagesImages/15.jpg", newimg)
            self.writeimg = False
        return newimg
