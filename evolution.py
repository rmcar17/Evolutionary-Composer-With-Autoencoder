import os

import numpy as np

from constants import PARAM_SIZE
from music_generator import MusicGenerator

class Evolver():
    def __init__(self):
        self.MuseGen = MusicGenerator()
        
        self.population_size = 8
        
        self.note_freq_low = 0.2
        self.note_freq_high = 0.4
        
        self.freq_mut_chance = 0.2
        self.freq_mut_factor = 0.02
        
        self.space_mut_chance = 0.1
        self.space_mut_factor = 0.08
    
    def initialise_population(self):
        self.genome = np.empty((self.population_size, PARAM_SIZE + 1))
        
        self.genome[:,0] = np.random.uniform(self.note_freq_low, self.note_freq_high, size=(self.population_size)) 
        self.genome[:,1:] = np.random.normal(size=(self.population_size, PARAM_SIZE))

        self.ids = np.arange(self.population_size)
        self.max_id = self.ids.max()

    def generate_population_songs(self):
        self.MuseGen.make_songs(self.genome[:,1:], self.genome[:,0], self.ids, savepath="tempSongs/")
    
    def cull_population(self, kill_ids):
        kill_ids = np.array(kill_ids)
        for file_id in kill_ids:
            os.remove("tempSongs/" + str(file_id) + ".midi")

        survivors = np.where(~np.isin(self.ids, kill_ids))

        self.ids = self.ids[survivors]
        self.genome = self.genome[survivors]
        

    def reproduce_population(self):
        new_population = np.empty((self.population_size, PARAM_SIZE + 1))
        new_population[:len(self.ids)] = self.genome

        new_ids = np.empty((self.population_size), dtype=np.int64)
        new_ids[:len(self.ids)] = self.ids

        pairs = set()
        for same_pair in [(i, i) for i in range(len(self.ids))]:
            pairs.add(same_pair)
        
        for i in range(len(self.ids), self.population_size):
            parents = tuple(np.random.randint(low=0, high=len(self.ids), size=2))
            while parents in pairs:
                parents = tuple(np.random.randint(low=0, high=len(self.ids), size=2))

            pairs.add(parents)
            pairs.add((parents[1], parents[0]))

            if len(pairs) == len(self.ids) ** 2:
                pairs.clear()
                for same_pair in [(i, i) for i in range(len(self.ids))]:
                    pairs.add(same_pair)

            # new_species = (new_population[parents[0]] + new_population[parents[1]]) / 2
            crossover = np.random.rand(PARAM_SIZE + 1) < 0.5
            new_species = np.empty(PARAM_SIZE + 1)
            new_species[crossover] = new_population[parents[0], crossover]
            new_species[~crossover] = new_population[parents[1], ~crossover]
            
            mutations = np.empty(shape=PARAM_SIZE + 1)
            
            mutations[0] = (np.random.uniform(size=1) < self.freq_mut_chance) * np.random.normal(scale=self.freq_mut_factor, size=1)
            mutations[1:] = (np.random.uniform(size=PARAM_SIZE) < self.space_mut_chance) * np.random.normal(scale=self.space_mut_factor, size=PARAM_SIZE)
            
            new_species += mutations
            
            new_population[i] = new_species
            
            self.max_id += 1
            new_ids[i] = self.max_id

        self.genome = new_population
        self.ids = new_ids
    
    def add_new_species(self):
        species = np.empty((1,181))
        
        species[0,0] = np.random.uniform(self.note_freq_low, self.note_freq_high)
        species[0,1:] = np.random.normal(size=PARAM_SIZE)

        self.genome = np.append(self.genome, species, axis=0)
        
        self.max_id += 1
        self.ids = np.append(self.ids, self.max_id)
        
        if len(self.genome) > self.population_size:
            self.population_size = len(self.genome)
    
    def save_species(self, save_ids):
        if len(save_ids) == 0:
            return
        save_ids = np.array(save_ids)
        to_save = np.where(np.isin(self.ids, save_ids))
        
        self.MuseGen.make_songs(self.genome[to_save,1:][0], self.genome[to_save,0][0], self.ids[to_save], savepath="savedSongs/")
    
    def get_sample_array(self, image_id):
        species_i = np.where(self.ids == image_id)
        
        species = self.MuseGen.get_note_array(self.genome[species_i, 1:][0])
        
        playing = np.where(species >= self.genome[species_i, 0])
        not_playing = np.where(species < self.genome[species_i, 0])
        species[playing] = 1
        species[not_playing] = 0
        return species


if __name__ == "__main__":
    evolver = Evolver()
    evolver.initialise_population()
    evolver.generate_population_songs()
    evolver.cull_population(np.array([1,2,7,3,6]))
    evolver.reproduce_population()
    # for i in range(20):
    #     evolver.add_new_species()
    evolver.generate_population_songs()
