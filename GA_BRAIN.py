from deap import base, creator, tools, algorithms
import numpy as np
import tetromino_GA as game
import copy

def trainSolver(board,fallingPiece):
	creator.create("FitnessMax", base.Fitness, weights=(-1.0,-1.0,1.0,1.0,-1.0)) 
	creator.create("Individual", list, fitness=creator.FitnessMax)
	toolbox = base.Toolbox()
	#toolbox.register("attr_real",np.random.randint,3)
	toolbox.register("individual", getInd, creator.Individual)# moves max
	toolbox.register("population", tools.initRepeat,list, toolbox.individual, 30)
	toolbox.register("evaluate", eval)
	toolbox.register("select",tools.selTournament, tournsize = 2)
	toolbox.register("mate", crossOver);
	#toolbox.register("mutate", tools.mutFlipBit, indpb = 0.1) # was .01 before
	toolbox.register("mutate", mutate)
	

	CXPB, MUTPB, NGEN = 0.05, 0.01, 50
	pop = toolbox.population()
	bestSoFar = (-9999999,-99999999,-99999999,-99999999)
	bestFit = []
	bests = []
	board = copy.deepcopy(board);
	fallingPiece = copy.deepcopy(fallingPiece)
	for g in range(NGEN):
		pop = algorithms.varAnd(pop,toolbox, cxpb = 0.5, mutpb = 0.5)
		for ind in pop:
			fit = game.processBoard(ind,board,fallingPiece)
			ind.fitness.values = fit

		best = tools.selBest(pop,k=1)
		bests.append(best[0])
	best = tools.selBest(bests,k=1);
	print best[0].fitness.values;
	return best[0]



def getInd(ind_class):
	direct =  np.random.randint(2); # 0 is left, 1 is right
	moves = np.random.randint(6); # 0 -> 5 moves
	rotation =  np.random.randint(4); # max is 4 rotation

	return ind_class([direct,moves,rotation]);

def crossOver(ind1,ind2):
	ind1[0] = (ind1[0] + 1) % 2;
	ind2[0] = (ind2[0] + 1) % 2;
	return ind1,ind2;

def mutate(individual):
	individual = copy.deepcopy(individual)
	if(np.random.rand() < 0.8):
		individual[1] = (individual[1]+1) % 6;

	if(np.random.rand() < 0.4):
		individual[2] = (individual[2]+1) % 4;

	return individual,



