'''Run this file to run the application'''
from MainUI import MainUI
from CNN import CNN
from KNN import KNN
import os
# Change the model type variable value to "CNN" to use the Convolutional Neural Network
# Change the model type variable value to "KNN" to use the K Nearest Neighbours Classifier
modeltype = "KNN"
# Checking if the KNN or CNN file is present
# If not present, then generate the required file
if modeltype == "KNN":
    if os.path.exists("knn.sav"):
        pass
    else:
        print("Saved KNN Classifier not found....")
        print("Downloading MNIST Data, training KNN classifier and saving as knn.sav......")
        print("Kindly wait for a few minutes............")
        knnobj = KNN(3)
        knnobj.skl_knn()
else:
    if os.path.exists("cnn.hdf5"):
        pass
    else:
        print("cnn.hdf5 not found...")
        print("Loading MNIST Data, training CNN and saving as cnn.hdf5.....")
        print("Kindly wait a few minutes.........")
        cnnobj = CNN()
        cnnobj.build_and_compile_model()
        cnnobj.train_and_evaluate_model()
        cnnobj.save_model()
MainUIobj = MainUI(modeltype)
MainUIobj.mainloop()
MainUIobj.cleanup()
