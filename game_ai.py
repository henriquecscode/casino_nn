import math
import numpy as np
import random
from stats import Stats
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam #Shouldn't need this since we are not going to use training

class GameAi (object):

    layers = [6,10,10,3]
    DATA_LEN = 20

    def __init__(self, model = None):

        if model is None:
            self.nn = self.model()
        else:
            self.nn = model
        self.getLayers()
        self.fitness = 0
        self.reset()

    def reset(self):
        #Specific to ai game state data
        self.prediction = None
        self.balance = 0

        #To calculate fitness
        self.game_state = None


        #Stats (Used to prediction)
        self.wins = []
        self.bet_amount = Stats(20)
        self.bet_number = Stats(20)
        self.losses_in_a_row = 0


        #Stats (Used just for debug)
        self.record_number = []
        self.record_amount = []

    def model(self):
        "returns a neural network for training"
        inputs = Input(shape=[self.layers[0]], name='input')
        network = Dense(self.layers[1], activation='sigmoid')(inputs)
        for i in range(2, len(self.layers) - 1):
            network = Dense(self.layers[i], activation='sigmoid')(network)
    
        #Output layer: Number, Wage
        network = Dense(self.layers[len(self.layers)-1], activation='linear')(network)

        model = Model(inputs=inputs, outputs=network)
        opt = Adam(0.01)
        model.compile(loss='mean_squared_error', optimizer=opt, metrics=['mse'])
        
        return model
        
    def betResult(self, profit):

        self.balance += profit
        if profit < 0:
            self.losses_in_a_row += 1
        else:
             self.losses_in_a_row = 0
        pass
        #deal with bet result
    
    def askForBet(self, game_state):
        bet_state = self.getBetState(game_state)

        bet_state = np.array([bet_state])
        self.prediction = self.nn.predict(bet_state)

        #predition = [number, wage, if we are betting the number will be lower]
        #self.prediction.append(1) #for now, the ai only decides number and wage

        number = abs(self.prediction[0][0] * 100)
        number = 5 if number < 5 else 96 if number > 96 else number
        number = round(number)
        wage = abs(self.prediction[0][1])
        lower = self.prediction[0][2]

        self.bet_amount.add(wage)
        self.bet_number.add(number)
        self.record_amount.append(wage)
        self.record_number.append(number)

        return [number, wage, lower]

    def getBetState(self, game_state):
        game_state.extend([self.losses_in_a_row, self.bet_amount.getAverage(), self.bet_number.getStdev()])
        return game_state


    def reproduce(self, ai):
        new_weights = []
        for x in range(len(self.weights)):
            new_weights.append(self.weights[x] if random.random() > 0.5 else ai.weights[x])
            #Randomizes betweeen a weight from this ai or from the one it is beeing reproduced with
            
        return new_weights
        
    def decompressWeights(self):
        weights = self.nn.get_weights()
        new_weights = []
        for x in range(len(weights)):
            if(x%2 == 0):
                layer = weights[x]
                for node in layer:
                    for conn in node:
                        new_weights.append(conn)
        self.weights = new_weights
    
    
    def compressWeights(self, weights):
        
        counter = 0
        new_weights = []
        for i in range(len(self.layers)-1):
            layer_weights = []
            for j in range(self.layers[i]):
                node_weights = []
                for k in range(self.layers[i+1]):
                    node_weights.append(weights[counter])
                    counter += 1
                layer_weights.append(node_weights)
            new_weights.append(np.array(layer_weights))
            new_weights.append(np.zeros(self.layers[i+1]))
        return new_weights
        
    def setWeights(self, new_weights):
        compressed_weights = self.compressWeights(new_weights)
        self.nn.set_weights(compressed_weights)
    

    def getLayers(self):
        weights = self.nn.get_weights()
        layers = []
        layers.append(len(weights[0]))
        for x in range(len(weights)):
            if x % 2 == 0:
                layers.append(np.size(weights[x][0]))
        print(layers)
