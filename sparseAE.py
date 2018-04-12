# -*- coding: utf-8 -*-
"""
Created on Mon Apr  9 15:55:05 2018

@author: Mona Hajimomeni
"""
#
# I am using implementation of sparse autoencoder by Zhi Wei
#
# ==============================================================================
# This is an example of using Tensorflow to build Sparse Autoencoder
# for representation learning.
# It is the implementation of the sparse autoencoder for
#        https://web.stanford.edu/class/cs294a/sparseAutoencoder_2011new.pdf
#
# For any enquiry, please contact Dr. Zhiwei Lin  at Ulster University
#       http://scm.ulster.ac.uk/zhiwei.lin/
#
#
# ==============================================================================
import tensorflow as tf
import matplotlib.pyplot
import math
import numpy as np




class FeedforwardSparseAutoEncoder():
    '''
      This is the implementation of the sparse autoencoder for https://web.stanford.edu/class/cs294a/sparseAutoencoder_2011new.pdf
    '''
    def __init__(self, n_input, n_hidden,  rho=0.01, alpha=0.0001, beta=3, activation=tf.nn.sigmoid, optimizer=tf.train.AdamOptimizer()):
        self.n_input=n_input
        self.n_hidden=n_hidden
        self.rho=rho  # sparse parameters
        self.alpha =alpha
        self.beta=beta
        self.optimizer=optimizer
        self.activation = activation

        self.W1=self.init_weights((self.n_input,self.n_hidden))
        self.b1=self.init_weights((1,self.n_hidden))

        self.W2=self.init_weights((self.n_hidden,self.n_input))
        self.b2= self.init_weights((1,self.n_input))
        init = tf.global_variables_initializer()
        self.sess = tf.Session()
        self.sess.run(init)

    def init_weights(self,shape):
        r= math.sqrt(6) / math.sqrt(self.n_input + self.n_hidden + 1)
        weights = tf.random_normal(shape, stddev=r)
        return tf.Variable(weights)

    def encode(self,X):
        l=tf.matmul(X, self.W1)+self.b1
        return self.activation(l)

    def decode(self,H):
        l=tf.matmul(H,self.W2)+self.b2
        return self.activation(l)


    def kl_divergence(self, rho, rho_hat):
        return rho * tf.log(rho) - rho * tf.log(rho_hat) + (1 - rho) * tf.log(1 - rho) - (1 - rho) * tf.log(1 - rho_hat)

    def regularization(self,weights):
        return tf.nn.l2_loss(weights)

    def loss(self,X):
        H = self.encode(X)
        rho_hat=tf.reduce_mean(H,axis=0)   #Average hidden layer over all data points in X, Page 14 in https://web.stanford.edu/class/cs294a/sparseAutoencoder_2011new.pdf
        kl=self.kl_divergence(self.rho, rho_hat)
        X_=self.decode(H)
        diff=X-X_
        cost= 0.5*tf.reduce_mean(tf.reduce_sum(diff**2,axis=1))  \
              +0.5*self.alpha*(tf.nn.l2_loss(self.W1) + tf.nn.l2_loss(self.W2))   \
              +self.beta*tf.reduce_sum(kl)
        return cost

    def training(self,training_data,  n_iter=100):
        X=tf.placeholder("float",shape=[None,training_data.shape[1]])
        print(training_data.shape[1])
        var_list=[self.W1,self.W2]
        loss_=self.loss(X)
        train_step=tf.contrib.opt.ScipyOptimizerInterface(loss_, var_list=var_list, method='L-BFGS-B',   options={'maxiter': n_iter})
        train_step.minimize(self.sess, feed_dict={X: training_data})
        print("done")


def visualizeW1(images, vis_patch_side, hid_patch_side, iter, file_name="trained_"):
    """ Visual all images in one pane"""

    figure, axes = matplotlib.pyplot.subplots(nrows=hid_patch_side, ncols=hid_patch_side)
    index = 0

    for axis in axes.flat:
        """ Add row of weights as an image to the plot """

        image = axis.imshow(images[index, :].reshape(vis_patch_side, vis_patch_side),
                            cmap=matplotlib.pyplot.cm.gray, interpolation='nearest')
        axis.set_frame_on(False)
        axis.set_axis_off()
        index += 1

    """ Show the obtained plot """
    file=file_name+str(iter)+".png"
    matplotlib.pyplot.savefig(file)
    print("Written into "+ file)
    matplotlib.pyplot.close()


# from tensorflow.examples.tutorials.mnist import input_data
# mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)


# ======================================    
# Loading our lung cancer data
# ======================================
output_path = "D:/Mona's files/Kaggle/Lung cancer/"

# images are resized to be able to run the network with sufficient memory
input_images = np.load(output_path+"comp_images_1.npy").astype(np.float32)
input_vectors = np.reshape(input_images, [365,4900])

# convert it to a tensor
# lung_tensor = tf.convert_to_tensor(masked_images, dtype = tf.float32)


n_inputs=4900 # 279 by 279
n_hidden=100
start=0
# the length of list of mnist images, for us there is 365 CT slices
lens=365
learning_rate=0.1

# this is an instance for this class
sae=   FeedforwardSparseAutoEncoder(n_inputs,n_hidden)
n_iters=4001
# now it is using the training attribute of the class
# sae.training(mnist.train.images[start:start+lens],n_iter=n_iters)
sae.training(input_vectors[start:start+lens],n_iter=n_iters)


# After training the model, an image of the representations (W1) will be saved
# Please check trained4000.png for example
images=sae.W1.eval(sae.sess)
images=images.transpose()
visualizeW1(images,70,10,n_iters)