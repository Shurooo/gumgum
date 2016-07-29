from sklearn.naive_bayes import BernoulliNB
import Get_Data as gd
import Predict_Module as predm
import Test_Module as testm


class BernoulliNBWrapper:
    def __init__(self, class_prior=None):