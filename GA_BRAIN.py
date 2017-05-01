from deap import base, creator, tools, algorithms
import numpy as np
import tetromino_GA as game
import copy

def trainSolver(board,fallingPiece):
	creator.create("FitnessMax", base.Fitness, weights=(-1.0,-1.0,-1.0,1.0)) 
	creator.create("Individual", list, fitness=creator.FitnessMax)
	toolbox = base.Toolbox()
	#toolbox.register("attr_real",np.random.randint,3)
	toolbox.register("individual", getInd, creator.Individual)# moves max
	toolbox.register("population", tools.initRepeat,list, toolbox.individual, 20)
	toolbox.register("evaluate", eval)
	toolbox.register("select",tools.selTournament, tournsize = 2)
	toolbox.register("mate", crossOver);
	#toolbox.register("mutate", tools.mutFlipBit, indpb = 0.1) # was .01 before
	toolbox.register("mutate", mutate)
	

	CXPB, MUTPB, NGEN = 0.05, 0.01, 150
	pop = toolbox.population()
	bestFit = []
	bests = []
	for g in range(NGEN):
		pop = algorithms.varAnd(pop,toolbox, cxpb = 0.1, mutpb = 0.1)
		for ind in pop:
			newBoard = copy.deepcopy(board)
			fit = game.processBoard(ind,newBoard,fallingPiece)
			ind.fitness.values = fit
		best = tools.selBest(pop,k=1)
		bests.append(best[0])
	best = tools.selBest(bests,k=1);
	print best[0].fitness.values;
	return best[0]

def getInd(ind_class):
	direct =  np.random.randint(2); # 0 is left, 1 is right
	moves = np.random.randint(6); # 0 -> 4 moves
	rotation =  np.random.randint(4); # max is 4 rotation

	return ind_class([direct,moves,rotation]);

def crossOver(ind1,ind2):
	ind1[0] = (ind1[0] + 1) % 2;
	ind2[0] = (ind2[0] + 1) % 2;
	return ind1,ind2;

def mutate(individual):
	individual = copy.deepcopy(individual)
	if(np.random.rand() < 0.5):
		individual[1] = (individual[1]+1) % 6;

	if(np.random.rand() < 0.05):
		individual[2] = (individual[1]+1) % 4;

	return individual,



