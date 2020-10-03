import random
import statistics
import multiprocessing as mp
import matplotlib.pyplot as plt
from collections import deque
import numpy as np
import sys, argparse
from stats import Stats
from genetic_algorithm import Population

random.seed()

class Casino:

    NO_ITERATIONS = 1000
    NO_GENERATIONS = 50
    TEST_ITERATIONS = 100
    INITIAL_ITERATIONS = 1000
    DATA_LEN = 1000
    pop = None
    rng = 0
    KEYS = ["-training", "-pop_size", "-initializion_size"]
    PAYOUTS = {5: 24.6250, 6: 19.7, 7: 16.4166, 8: 14.0714, 9: 12.3125, 10: 10.9444, 11: 9.8500, 12: 8.9545, 13: 8.2083, 14: 7.5769, 15: 7.0357, 16: 6.5666, 17: 6.1562, 18: 5.7941, 19: 5.4722, 20: 5.1842, 21: 4.9250, 22: 4.6904, 23: 4.4772, 24: 4.2826, 25: 4.1041, 26: 3.9400, 27: 3.7884, 28: 3.6481, 29: 3.5178, 30: 3.3965, 31: 3.2833, 32: 3.1774, 33: 3.0781, 34: 2.9848, 35: 2.8970, 36: 2.8142, 37: 2.7361, 38: 2.6621, 39: 2.5921, 40: 2.5256, 41: 2.4625, 42: 2.4024, 43: 2.3452, 44: 2.2906, 45: 2.2386, 46: 2.1888, 47: 2.1413, 48: 2.0957, 49: 2.0520, 50: 2.0102,
               51: 1.9700, 52: 1.9213, 53: 1.8942, 54: 1.8584, 55: 1.8240, 56: 1.7909, 57: 1.7589, 58: 1.7280, 59: 1.6982, 60: 1.6694, 61: 1.6416, 62: 1.6147, 63: 1.5887, 64: 1.5634, 65: 1.5390, 66: 1.5153, 67: 1.4924, 68: 1.4701, 69: 1.4485, 70: 1.4275, 71: 1.4071, 72: 1.3873, 73: 1.3680, 74: 1.3493, 75: 1.3310, 76: 1.3133, 77: 1.2960, 78: 1.2792, 79: 1.2628, 80: 1.2468, 81: 1.2312, 82: 1.2160, 83: 1.2012, 84: 1.1867, 85: 1.1726, 86: 1.1588, 87: 1.1453, 88: 1.1321, 89: 1.1193, 90: 1.1067, 91: 1.0944, 92: 1.0824, 93: 1.0706, 94: 1.0591, 95: 1.0478, 96: 1.0368}


    def __init__(self, args):
        definitions = self.definitions(args)
        self.execute(definitions)

    def definitions(self, args):
        definitions = []
        if args.training == None:
            training = ""
            while training not in ["t", "e"]:
                training = input("enter t for training or e for examination/test")
            training = training == "t"
        else:
            training = args.training

        if args.initialized == None:
            num_ais = -1
            while num_ais < 0 or num_ais > 10:
                num_ais = int(input("how many ais you want to already be initalized"))
        else:
            initialized = args.initialized

        if args.pop_size == None:
            pop_size = -1
            while pop_size < 0 or pop_size > 100:
                pop_size = int(input("How many ais the population should be made of"))
        else:
            pop_size = args.pop_size

        return [training, initialized, pop_size]
    def execute(self, definitions):
        training, initialized, pop_size = definitions
        self.pop = Population(save_size = initialized, population_size=pop_size)
        self.setupInitialState()

        if training:
            self.runTraining()
        else:
            self.runTest()

        self.results()

    def setupInitialState(self):
        
        self.data_results = Stats(self.DATA_LEN)


        print('Setting initial state')
        for _ in range(self.INITIAL_ITERATIONS):
            self.getRandom()
            self.data_results.add(self.rng)

        print('Initial state set')

    def runTraining(self):
        for i in range(self.NO_GENERATIONS):
            print('Generation', i+1 )
            self.runGeneration()
        self.pop.savePop()

    def runTest(self):
        for _ in range(self.TEST_ITERATIONS):
            self.runAis()
        self.pop.fitness()

    def runGeneration(self):
        for _ in range(self.NO_ITERATIONS):
            self.runAis()
        self.pop.updateAis()
        
    def runAis(self):
        self.getRandom()
        self.updateStats()
        self.game_state = self.getGameState()

        '''
        #Multiprocessing
        pool = mp.Pool(mp.cpu_count())
        pool.map_async(self.handleAiBet, [ai for ai in self.pop.population])
        pool.close()
        pool.join()
        '''
        #No multiprocessing
        self.handleAllBet()

    def handleAllBet(self):
        for ai in self.pop.population:
            self.handleAiBet(ai)

    def handleAiBet(self, ai):
        bet = ai.askForBet(self.game_state[:])
        profit = self.decideBet(bet)
        ai.betResult(profit)

    def decideBet(self, bet):
        number = bet[0]
        wage = bet[1]
        lower = bet[2]
        if lower > 0: # We win if obtain a lower number
            return -wage if number >= self.rng else (self.PAYOUTS[number]-1) * wage
        return -wage if number <= self.rng else (self.PAYOUTS[number] - 1) * wage

    def getRandom(self):
        self.rng = random.randint(1, 100)

    def getGameState(self):
        return [self.data_results.getAverage(), self.data_results.getStdev(), self.data_results.getSkew()]

    def updateStats(self):
        self.data_results.add(self.rng)
        # Sets of stats that are kept about the progress of the chain of RNGs

    def results(self):
        print("Finished execution")
        print([x.balance for x in self.pop.population])
        #input()
        #print([x.record_number for x in self.pop.population])
        #input()
        #print([x.record_amount for x in self.pop.population])
        plt.plot([i for i in range(len(self.pop.population[0].record_balance))], np.transpose([x.record_balance for x in self.pop.population]))
        plt.show()
        input("Enter any string to continue")

parser=argparse.ArgumentParser()
parser.add_argument('-training', type=lambda x: (str(x).lower() in ['true','1', 'yes']), default=None)
parser.add_argument('-initialized', type = int, default = None)
parser.add_argument('-pop_size', type=int, default = None)
args = parser.parse_args()

Casino(args)
exit()
