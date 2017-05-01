from deap import base, creator, tools, algorithms
import numpy as np
import tetromino_GA as game
import copy

def trainSolver(board,fallingPiece):
	creator.create("FitnessMax", base.Fitness, weights=(-1.0,-1.0,1.0)) 
	creator.create("Individual", list, fitness=creator.FitnessMax)
	toolbox = base.Toolbox()
	toolbox.register("attr_real",np.random.randint,3)
	toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_real, 5)# moves max
	toolbox.register("population", tools.initRepeat,list, toolbox.individual, 300)
	toolbox.register("evaluate", eval)
	toolbox.register("select",tools.selTournament, tournsize = 2)
	toolbox.register("mate", tools.cxOnePoint);
	toolbox.register("mutate", tools.mutFlipBit, indpb = 0.2) # was .01 before
	
	CXPB, MUTPB, NGEN = 0.05, 0.01, 50
	pop = toolbox.population()

	bestSoFar = (-9999999,-99999999,-99999999)
	bestFit = []
	for g in range(NGEN):
		pop = algorithms.varAnd(pop,toolbox, cxpb = CXPB, mutpb = 0.05)
		for ind in pop:
			newBoard = copy.deepcopy(board)
			fit = game.processBoard(ind,newBoard,fallingPiece)
			ind.fitness.values = fit
		best = tools.selBest(pop,k=1)
		if best[0].fitness.values > bestSoFar:
			bestSoFar = best[0].fitness.values;
			bestFit = best[0]
	print bestSoFar
	return bestFit