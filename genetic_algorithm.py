import random
from game_ai import GameAi
from datetime import datetime
from tensorflow.keras.models import load_model

    #https://www.youtube.com/watch?v=G8KJWONEeGo
'''
#############
TODO
Make a pointer to the 3d array used to iterate throught the weights that are already in a list
    Use dictionary with int indexes pointing to the each of the elements of the list
    Use that dictionary to point to the actual reference of the ai.mode.layers instead?
        It won't be that much less efficient and a lot easier to handle
        Just keep in mind that if I rewrite it by assigning a new model's weights I might lose the dic reference (doing self.models_weights = self.model.get_weights() might cut the dic usage)
Research ndenumerate
##############
'''

class Population(object):
    population_size = 10
    fixed_individuals = 0 #Amount of individuals that get through to the next generation
    mutation_rate = 0.05
    
    #Fitness multipliers

    save_path = 'neurals/'
    
    def __init__(self, save_size = 0):

        print('Creating population')
        #Creates the population
        self.population = self.loadPop(size = save_size)
        if(len(self.population) > self.population_size):
            print('Loaded', len(self.population), 'ais.', (len(self.population) - self.population_size) + 'more than intended')
            print('Now executing with an incremented number of ais')
            self.population_size = len(self.population)
        elif(len(self.population) == self.population_size):
            print('Sucessfully loaded all of the', self.population_size, 'ais')
        else: # len(self.population) < self.population_size:
            print('Loaded',  len(self.population), 'ais','\n' + 'now creating', (self.population_size - len(self.population)), 'ais')
            self.population.extend(self.createPopulation(self.population_size - len(self.population)))
            
        print('Population created')
        print(self.population[0].nn.summary())


#        self.multi_game = MultiGame(self.population_size, self.population)
        self.generation = 0
        self.fitness_sum = 0
        self.relative_probability = []
        
        self.best_fitness = 0
        self.best_gameai = None

    def createPopulation(self, size):
        population = []
        for _ in range(size):
            population.append(GameAi())

        return population
            
    def updateAis(self):
            self.decompressWeights()
            self.fitness()
            self.reproduce()
            for ai in self.population:
                ai.reset()
            self.generation += 1
            
    
    def fitness(self):
        
        min_balance = min([x.balance for x in self.population])
        max_balance = max([x.balance for x in self.population])
        if max_balance > 0:
            print('You did it, you crazy son of a bitch you did it')
            print([x.balance > 0 for x in self.population].count(True))
        self.fitness_sum = 0
        self.relative_probability = []
        for x,ai  in enumerate(self.population):
            ai_fitness = ai.balance - min_balance

            self.population[x].fitness = 1 + ai_fitness #1 just not to crash
            self.fitness_sum += self.population[x].fitness
            if(ai_fitness > self.best_fitness):
                self.best_fitness = ai_fitness
                self.best_gameai = self.population[x]
        self.population.sort(key = self.sortByFitness) 
        
        fitness_acumulator = 0
        for x, ai  in enumerate(self.population):
            fitness_acumulator += ai.fitness
            self.population[x].fitness_absolute = fitness_acumulator
 
        #To use in the choice of a parent
        for individual in self.population:
            self.relative_probability.append(individual.fitness / self.fitness_sum)

    def sortByFitness(self, ai):
        return ai.fitness
        
        
    def getScore(self, game_score):
        print(game_score)
        time, enemies_hit, enemies_destroyed, bullets, jumps = game_score
        
        score = time  * self.time_multiplier + enemies_hit * self.hit_multiplier + enemies_destroyed * self.destroyed_multiplier
        score /= (bullets * self.bullets_multiplier + jumps + self.jumps_multiplier)
        return score
            
    def reproduce(self):
        
        next_gen_weights = []
        
        #Creates a 1d array by crossing the weights of certain individuals
        for x in range(self.population_size - self.fixed_individuals): #Amount that are going to get crossovered
            parenta = self.chooseParent()
            parentb = self.chooseParent()
            
            childs_weights = parenta.reproduce(parentb)
            next_gen_weights.append(childs_weights)
            
        #Creates a 1d array from the best individual's weights
        for x in range(self.fixed_individuals):
            best_individual = self.population[x]
            best_individuals_weights = []
            for best_individuals_weight in best_individual.weights:
                best_individuals_weights.append(best_individuals_weight)
            next_gen_weights.append(best_individuals_weights) #Apends the best to the new generation
            
        #Mutation and update
        for x in range(len(next_gen_weights)):
            self.population[x].setWeights(self.mutate(next_gen_weights[x]))
            
    #https://www.youtube.com/watch?v=G8KJWONEeGo
    def chooseParent(self):

        randomNumber = random.random() * self.fitness_sum
        for individual in self.population:
            if(randomNumber < individual.fitness_absolute):
                return individual
            
            randomNumber -= individual.fitness
            
        print('Unable to choose parent. Using index 0')
        return self.population[0]
    
    
    def decompressWeights(self):
        for individual in self.population:
            individual.decompressWeights()
            
    def mutate(self, weights):
        new_weights = []
        for weight in weights:
            chance = random.random()
            if(chance < self.mutation_rate):
                #Does mutate
                new_weight = (0.5 - random.random()) * 2 #Value between -1 and 1
                new_weights.append(new_weight)
                #How to randomize a keras weight?
            else:
                #Doesn't mutate
                new_weights.append(weight)
        
        return new_weights
    
    def savePop(self, path = None):
        
        if path is None:
            path = self.save_path
        for x in range(len(self.population)):
            individual = self.population[x]
            individual.nn.save(path + 'neural_' + str(x) + datetime.now().strftime() + '.h5')
          
    def loadPop(self, path= None, size = 0):
        loaded_ai = []
        if path is None:
            path = self.save_path
            
        if size == -1:
            size = self.population_size
            #Should be until the try loop crashes
            #Changed the for loop to a while loop?
        try:
            for i in range(size): #Does until crashing because there are no more ais to load
                full_path = path + 'neural_' + str(len(loaded_ai)) + '.h5'
                nn = load_model(full_path)
                new_ai = GameAi(nn)
                loaded_ai.append(new_ai)
        except:
            pass
        
        return loaded_ai
