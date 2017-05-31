from random import Random


class Utils:
    random = Random()

    @staticmethod
    def probability_check(probability):
        # Probability from 0 to 100
        return Utils.random.randint(0, 100) < probability

    @staticmethod
    def rand_int(minimum, maximum):
        return Utils.random.randint(minimum, maximum)

    @staticmethod
    def clamp_mod(value, maximum):
        # Limits a value in the range 0, maximum-1. if value is -1 it will become maximum-1
        if value >= maximum:
            value -= maximum
        if value < 0:
            value += maximum

        return value

    @staticmethod
    def clamp(value, minimum, maximum):
        if value >= maximum:
            value = maximum
        if value <= minimum:
            value = minimum

        return value
