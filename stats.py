from collections import deque
import math

class Stats:

    #https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance
    #https://en.wikipedia.org/wiki/Skewness#Pearson's_moment_coefficient_of_skewness


    def __init__(self, size):
        self.values = deque([])
        self.size = size
        self.average = 0
        self.sum = 0
        self.sum_squares = 0
        self.sum_cubes = 0
        self.stdev_mul = 1 / size / (size-1)
        self.stdev = 0
        self.skew = 0

    def add(self, value):
        if len(self.values) == self.size:
            first = self.values.popleft()
            self.sum -= first
            self.sum_squares -= first ** 2
            self.sum_cubes -= first ** 3
        self.values.append(value)


        self.sum += value
        self.sum_squares += value ** 2
        self.sum_cubes += value ** 3

        self.average = self.sum / self.size
        self.stdev = math.sqrt(max([self.stdev_mul * (self.size * self.sum_squares - self.sum ** 2), 0.001]))
        self.skew = (self.sum_cubes / self.size - 3 * self.average * self.stdev**2  - self.average ** 3 ) / self.stdev ** 3

    def getAverage(self):
        return self.average

    def getStdev(self):
        return self.stdev

    def getSkew(self):
        return self.skew