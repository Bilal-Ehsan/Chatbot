from simpful import *


FS = FuzzySystem(show_banner=False)  # Fuzzy system object

S_1 = FuzzySet(function=Triangular_MF(a=0, b=0, c=5), term='weak')
S_2 = FuzzySet(function=Triangular_MF(a=0, b=5, c=10), term='average')
S_3 = FuzzySet(function=Triangular_MF(a=5, b=10, c=10), term='high')
FS.add_linguistic_variable('Strength', LinguisticVariable([S_1, S_2, S_3], concept='How strong', universe_of_discourse=[0,10]))

F_1 = FuzzySet(function=Triangular_MF(a=0, b=0, c=10), term='slow')
F_2 = FuzzySet(function=Triangular_MF(a=0, b=10, c=10), term='rapid')
FS.add_linguistic_variable('Speed', LinguisticVariable([F_1, F_2], concept='How fast', universe_of_discourse=[0,10]))

T_1 = FuzzySet(function=Triangular_MF(a=0, b=0, c=10), term='low')
T_2 = FuzzySet(function=Triangular_MF(a=0, b=10, c=20), term='medium')
T_3 = FuzzySet(function=Trapezoidal_MF(a=10, b=20, c=25, d=25), term='high')
FS.add_linguistic_variable('Threat', LinguisticVariable([T_1, T_2, T_3], universe_of_discourse=[0,25]))
