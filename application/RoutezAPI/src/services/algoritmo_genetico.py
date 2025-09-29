from services.distancia import Distancia
import copy
from services.tempo_execucao import TempoExecucao
from core.abstract.algoritmo_base import AlgoritmoBase
import numpy as np
from typing import List, Tuple
from core.dto.algoritmos_dto import PontoDTO
import random
from services.sequencia_execucao import SequenciaExecucao
from core.enum.tipos_algoritmos import TipoAlgoritmo
from services.metrica_preco import MetricaPreco
from services.metrica_memoria import UsoMemoria

class AlgoritmoGenetico(AlgoritmoBase):
    
    POPULATION_SIZE = 100
    NUM_GENERATIONS = 500
    MUTATION_RATE = 0.02
    TOURNAMENT_SIZE = 5 
    ELITISM_COUNT = 1 
    TIPO_ALGORITMO = TipoAlgoritmo.GENETICO 

    
    def _executar_logica_algoritmo(self, dist_matrix: np.ndarray, pontos: List[PontoDTO]) -> Tuple[List[PontoDTO], float]:
        random.seed = 14
        population = self.initialize_population(self.POPULATION_SIZE, len(pontos))
        best_overall_route = None
        best_overall_distance = float('inf')

        for generation in range(self.NUM_GENERATIONS):
            fitnesses = [self.calculate_fitness(individual, dist_matrix) for individual in population]

            current_best_index = np.argmin(fitnesses)
            current_best_route = population[current_best_index]
            current_best_distance = fitnesses[current_best_index]

            if current_best_distance < best_overall_distance:
                best_overall_distance = current_best_distance
                best_overall_route = copy.deepcopy(current_best_route) # Garante que copiamos o objeto

            new_population = []

            sorted_population_with_fitness = sorted(zip(population, fitnesses), key=lambda x: x[1])
           
            for i in range(self.ELITISM_COUNT):
                new_population.append(copy.deepcopy(sorted_population_with_fitness[i][0]))

            while len(new_population) < self.POPULATION_SIZE:
                parent1 = self.tournament_selection(population, fitnesses, self.TOURNAMENT_SIZE)
                parent2 = self.tournament_selection(population, fitnesses, self.TOURNAMENT_SIZE)
                
                child1, child2 = self.order_crossover(parent1, parent2)
                
                child1 = self.swap_mutation(child1, self.MUTATION_RATE)
                child2 = self.swap_mutation(child2, self.MUTATION_RATE)
                
                new_population.append(child1)
                if len(new_population) < self.POPULATION_SIZE: 
                    new_population.append(child2)
            
            population = new_population

            if generation % 50 == 0:
                print(f"Geração {generation}: Melhor distância = {best_overall_distance:.2f}, Rota = {best_overall_route}")

        print("\n--- Resultados Finais ---")
        print(f"Melhor rota encontrada: {best_overall_route}")
        print(f"Distância total da melhor rota: {best_overall_distance:.2f}")
        
        castedRoute : List[PontoDTO] = []
        
        [castedRoute.append(pontos[cromossomo]) for cromossomo in best_overall_route]
        castedRoute.append(castedRoute[0])

        print(castedRoute)
        
        return castedRoute, best_overall_distance
        
    def create_individual(self, n):
        cities = list(range(n))
        random.shuffle(cities) 
        return cities

    def tournament_selection(self, population, fitnesses, tournament_size):
        selected_individual = None
        best_fitness = float('inf') 
        
        for _ in range(tournament_size):
            candidate_index = random.randint(0, len(population) - 1)
            candidate = population[candidate_index]
            candidate_fitness = fitnesses[candidate_index]
            
            if candidate_fitness < best_fitness: 
                best_fitness = candidate_fitness
                selected_individual = candidate
                
        return selected_individual

    def order_crossover(self,parent1, parent2):
        size = len(parent1)
        child1 = [-1] * size
        child2 = [-1] * size

        start_index = random.randint(0, size - 1)
        end_index = random.randint(start_index, size - 1)

        child1[start_index:end_index+1] = parent1[start_index:end_index+1]
        child2[start_index:end_index+1] = parent2[start_index:end_index+1]

        current_parent2_pos = (end_index + 1) % size
        current_child1_pos = (end_index + 1) % size
        while -1 in child1:
            if parent2[current_parent2_pos] not in child1:
                child1[current_child1_pos] = parent2[current_parent2_pos]
                current_child1_pos = (current_child1_pos + 1) % size
            current_parent2_pos = (current_parent2_pos + 1) % size
        
        current_parent1_pos = (end_index + 1) % size
        current_child2_pos = (end_index + 1) % size
        while -1 in child2:
            if parent1[current_parent1_pos] not in child2:
                child2[current_child2_pos] = parent1[current_parent1_pos]
                current_child2_pos = (current_child2_pos + 1) % size
            current_parent1_pos = (current_parent1_pos + 1) % size

        return child1, child2

    def swap_mutation(self,chromosome, mutation_rate):
        if random.random() < mutation_rate:
            idx1, idx2 = random.sample(range(len(chromosome)), 2) 
            chromosome[idx1], chromosome[idx2] = chromosome[idx2], chromosome[idx1]
        return chromosome



    def initialize_population(self, size, cities_num):
        population = []
        for _ in range(size):
            population.append(self.create_individual(cities_num))
        return population


    def calculate_fitness(self, individual, distMatrix):
        total_distance = 0
        for i in range(len(individual) - 1):
            city_from = individual[i]
            city_to = individual[i+1]
            total_distance += distMatrix[city_from][city_to]
        
        
        total_distance += distMatrix[individual[-1]][individual[0]]
        
        return total_distance

    
def get_algoritmo_genetico() -> AlgoritmoGenetico:
    service =  AlgoritmoGenetico()
    service.adicionar_metrica(TempoExecucao())
    service.adicionar_metrica(SequenciaExecucao())
    service.adicionar_metrica(Distancia())
    service.adicionar_metrica(MetricaPreco(tipo_recurso='cpu')) # <--- NOVO
    service.adicionar_metrica(UsoMemoria())             # <--- NOVO
    # service.adicionar_metrica(ConvergenciaDistancia())  # <--- NOVO
    return service
        
    
    
    