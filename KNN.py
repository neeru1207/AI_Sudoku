'''This is a K Nearest Neighbours algorithm with k=3. This model is trained on the MNIST
handwritten digits dataset with 50,000 images for the training set and 10,000 for testing.
Then the model is saved using pickle as a knn.sav file '''
import numpy as np
from sklearn import datasets
from sklearn.metrics import classification_report
from sklearn.neighbors import KNeighborsClassifier
import pickle

k = 3
class KNN:

    def __init__(self, k):
        self.mnist = datasets.fetch_openml('mnist_784', data_home='mnist_dataset/')
        self.data, self.target = self.mnist.data, self.mnist.target
        # Make an array of indices the size of MNIST to use for making the data sets.
        # This array is in random order, so we can use it to scramble up the MNIST data
        self.indx = np.random.choice(len(self.target), 70000, replace=False)
        # Initialising the classifier
        self.classifier = KNeighborsClassifier(n_neighbors=k)

    # method for building the datasets to test with
    def mk_dataset(self, size):
        """makes a dataset of size "size", and returns that datasets images and targets
        This is used to make the dataset that will be stored by a model and used in
        experimenting with different stored dataset sizes
        """
        train_img = [self.data[i] for i in self.indx[:size]]
        train_img = np.array(train_img)
        train_target = [self.target[i] for i in self.indx[:size]]
        train_target = np.array(train_target)

        return train_img, train_target

    def skl_knn(self):
        """k: number of neighbors to use in classification
        test_data: the data/targets used to test the classifier
        stored_data: the data/targets used to classify the test_data
        """
        fifty_x, fifty_y = self.mk_dataset(50000)
        test_img = [self.data[i] for i in self.indx[60000:70000]]
        test_img1 = np.array(test_img)
        test_target = [self.target[i] for i in self.indx[60000:70000]]
        test_target1 = np.array(test_target)
        self.classifier.fit(fifty_x, fifty_y)

        y_pred = self.classifier.predict(test_img1)
        pickle.dump(self.classifier, open('knn.sav', 'wb'))
        print(classification_report(test_target1, y_pred))
        print("KNN Classifier model saved as knn.sav!")