import pygame
import numpy as np

from evolution import Evolver

# Initialise evolution
evolver = Evolver()
evolver.initialise_population()
evolver.generate_population_songs()

# Screen Parameters
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768

# Population Parameters
POP_WIDTH = 60
POP_HEIGHT = 40

POP_LEFT_BOUND = 0
POP_RIGHT_BOUND = int(SCREEN_WIDTH * 0.75)
POP_UP_BOUND = 0
POP_DOWN_BOUND = int(SCREEN_HEIGHT * 0.6) - 5

spaces_x = (((POP_RIGHT_BOUND - POP_LEFT_BOUND) // POP_WIDTH) + 1) // 2
offset_x = ((POP_RIGHT_BOUND - POP_LEFT_BOUND) - POP_WIDTH * (2 * spaces_x - 1)) // 2

spaces_y = (((POP_DOWN_BOUND - POP_UP_BOUND) // POP_HEIGHT) + 1) // 2
offset_y = ((POP_DOWN_BOUND - POP_UP_BOUND) - POP_HEIGHT * (2 * spaces_y - 1)) // 2
 
POP_BOXES = [pygame.rect.Rect(i, j, POP_WIDTH, POP_HEIGHT) for j in range(POP_UP_BOUND + offset_y, POP_DOWN_BOUND, 2 * POP_HEIGHT) for i in range(POP_LEFT_BOUND + offset_x, POP_RIGHT_BOUND, 2 * POP_WIDTH)]

species_selected = [False for i in range(len(POP_BOXES))]

# Control Parameters
CONTROLS = [("Select Save", "Save"), ("Select Kill", "Kill"), "Reproduce", "Random New", "+ Population Size", "- Population Size", "+ NF Mut Rate", "- NF Mut Rate", "+ Mut Rate", "- Mut Rate", "+ NF Mut Fac", "- NF Mut Fac", "+ Mut Fac", "- Mut Fac"]

CONTROLS_OUTLINE_WIDTH = 7

CONTROLS_LEFT_BOUND = POP_RIGHT_BOUND
CONTROLS_RIGHT_BOUND = SCREEN_WIDTH
CONTROLS_UP_BOUND = POP_UP_BOUND
CONTROLS_DOWN_BOUND = POP_DOWN_BOUND
CONTROL_HEIGHT = round(POP_DOWN_BOUND / len(CONTROLS) - CONTROLS_OUTLINE_WIDTH / len(CONTROLS))
CONTROL_BOXES = [pygame.rect.Rect(CONTROLS_LEFT_BOUND + CONTROLS_OUTLINE_WIDTH, CONTROLS_UP_BOUND + CONTROL_HEIGHT * i + CONTROLS_OUTLINE_WIDTH, CONTROLS_RIGHT_BOUND - CONTROLS_LEFT_BOUND - 2 * CONTROLS_OUTLINE_WIDTH, CONTROL_HEIGHT - CONTROLS_OUTLINE_WIDTH) for i in range(len(CONTROLS))]

control_selected = [False for i in range(len(CONTROLS))]

# Initialise Game
pygame.init()


# Colours
BACKGROUND_COLOUR = pygame.Color("#242038")

POPULATION_BACKGROUND_COLOUR = pygame.Color("#708B75")

POPULATION_COLOUR = pygame.Color("#D1E3DD")

POPULATION_OUTLINE_COLOUR = pygame.Color("#D1E3DD")
POPULATION_OUTLINE_COLOUR.a = 100

SPECIES_SELECTED_COLOUR = pygame.Color("#9067C6")

CONTROL_OUTLINE_COLOUR = pygame.Color("#9067C6")

CONTROL_COLOUR = pygame.Color("#8D86C9")
CONTROL_SELECTED_COLOUR = pygame.Color("#9067C6")

# Fonts
POP_FONT = pygame.font.SysFont("arial", 18)
CONTROL_FONT = pygame.font.SysFont("arial", 24)
CONTROL_FONT.set_bold(True)

# Set Screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Caption Screen
pygame.display.set_caption("Evolutionary Music Composer")

# Draw Population Background
def draw_population_background():
    pygame.draw.rect(screen, POPULATION_BACKGROUND_COLOUR, (POP_LEFT_BOUND, POP_UP_BOUND, POP_RIGHT_BOUND - POP_LEFT_BOUND, POP_DOWN_BOUND - POP_UP_BOUND))
    for box in POP_BOXES:
        pygame.draw.rect(screen, POPULATION_OUTLINE_COLOUR, box, 2)

# Draw Population
def draw_population():
    for i in range(len(evolver.ids)):
        text = POP_FONT.render(str(evolver.ids[i]), True, BACKGROUND_COLOUR)
        pygame.draw.rect(screen, SPECIES_SELECTED_COLOUR if species_selected[i] else POPULATION_COLOUR, POP_BOXES[i])
        screen.blit(text, (POP_BOXES[i].left + POP_BOXES[i].width // 2 - text.get_width() // 2, POP_BOXES[i].top + POP_BOXES[i].height // 2 - text.get_height() // 2))

# Draw Controls
def draw_controls():
    pygame.draw.rect(screen, CONTROL_OUTLINE_COLOUR, (CONTROLS_LEFT_BOUND, CONTROLS_UP_BOUND, CONTROLS_OUTLINE_WIDTH, CONTROLS_DOWN_BOUND - CONTROLS_UP_BOUND))
    pygame.draw.rect(screen, CONTROL_OUTLINE_COLOUR, (CONTROLS_RIGHT_BOUND - CONTROLS_OUTLINE_WIDTH, CONTROLS_UP_BOUND, CONTROLS_OUTLINE_WIDTH, CONTROLS_DOWN_BOUND - CONTROLS_UP_BOUND))
    pygame.draw.rect(screen, CONTROL_OUTLINE_COLOUR, (CONTROLS_LEFT_BOUND, CONTROLS_UP_BOUND, CONTROLS_RIGHT_BOUND - CONTROLS_LEFT_BOUND, CONTROLS_OUTLINE_WIDTH))
    for i, control_name in enumerate(CONTROLS):
        pygame.draw.rect(screen, CONTROL_OUTLINE_COLOUR, (CONTROLS_LEFT_BOUND, CONTROLS_UP_BOUND + CONTROL_HEIGHT * (i+1), CONTROLS_RIGHT_BOUND - CONTROLS_LEFT_BOUND, CONTROLS_OUTLINE_WIDTH))
        pygame.draw.rect(screen, CONTROL_SELECTED_COLOUR if control_selected[i] else CONTROL_COLOUR, CONTROL_BOXES[i])
        
        if isinstance(control_name, tuple):
            text = CONTROL_FONT.render(control_name[control_selected[i]], True, BACKGROUND_COLOUR)
        else:
            
            text = CONTROL_FONT.render(control_name, True, BACKGROUND_COLOUR)
        screen.blit(text, (CONTROL_BOXES[i].left + CONTROL_BOXES[i].width // 2 - text.get_width() // 2, CONTROL_BOXES[i].top + CONTROL_BOXES[i].height // 2 - text.get_height() // 2))

# Draw Stats
def draw_stats():
    texts =  []
    texts.append(POP_FONT.render("Population: " + str(evolver.population_size), True, POPULATION_BACKGROUND_COLOUR))
    texts.append(POP_FONT.render("Note Frequency Mut Rate: " + str(evolver.freq_mut_chance), True, POPULATION_BACKGROUND_COLOUR))
    texts.append(POP_FONT.render("Note Frequency Mut Factor: " + str(evolver.freq_mut_factor), True, POPULATION_BACKGROUND_COLOUR))
    texts.append(POP_FONT.render("Mut Rate: " + str(evolver.space_mut_chance), True, POPULATION_BACKGROUND_COLOUR))
    texts.append(POP_FONT.render("Mut Factor: " + str(evolver.space_mut_factor), True, POPULATION_BACKGROUND_COLOUR))

    for i, text in enumerate(texts):
        screen.blit(text, (POP_RIGHT_BOUND, POP_DOWN_BOUND + i * text.get_height()))


selecting_save = False
to_save = set()

selecting_kill = False
to_kill = set()

def convert_music(music_array):
    output = np.empty((*music_array.shape, 3))
    for i in range(output.shape[0]):
        for j in range(output.shape[1]):
            output[i, -j-1, :] = 255 if music_array[i, j] else 0
    return output

music_array = np.full(evolver.get_sample_array(1).shape, 0)
music = convert_music(music_array)

# Game Loop
running = True
while running:
    screen.fill(BACKGROUND_COLOUR)
    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for i in range(len(evolver.ids)):
                if POP_BOXES[i].collidepoint(event.pos):
                    if not (selecting_kill or selecting_save):
                        species_selected = [False for i in range(len(species_selected))]
                        species_selected[i] = True
                        pygame.mixer.music.load("tempSongs/" + str(evolver.ids[i]) + ".midi")
                        pygame.mixer.music.play(-1)
                        music = convert_music(evolver.get_sample_array(evolver.ids[i]))
                    else:
                        species_selected[i] = not species_selected[i]
                        if species_selected[i]:
                            if selecting_save:
                                to_save.add(evolver.ids[i])
                            elif selecting_kill:
                                to_kill.add(evolver.ids[i])
                        else:
                            if selecting_save:
                                to_save.remove(evolver.ids[i])
                            elif selecting_kill:
                                to_kill.remove(evolver.ids[i])
            for i, control in enumerate(CONTROL_BOXES):
                if control.collidepoint(event.pos):
                    pygame.mixer.music.stop()
                    if not any(control_selected[:i] + control_selected[i+1:]):
                        species_selected = [False for i in range(len(species_selected))]
                        control_selected[i] = not control_selected[i]
                        if i == 0:
                            selecting_save = control_selected[i]
                            if selecting_save:
                                to_save.clear()
                            else:
                                evolver.save_species(list(to_save))
                        elif i == 1:
                            selecting_kill = control_selected[i]
                            if selecting_kill:
                                to_kill.clear()
                            else:
                                evolver.cull_population(list(to_kill))
                        elif i == 2:
                            evolver.reproduce_population()
                            evolver.generate_population_songs()
                        elif i == 3 and len(evolver.ids) < len(POP_BOXES):
                            evolver.add_new_species()
                            evolver.generate_population_songs()
                        elif i == 4 and evolver.population_size < len(POP_BOXES):
                            evolver.population_size += 1
                        elif i == 5 and evolver.population_size > 2 and len(evolver.ids) < evolver.population_size:
                            evolver.population_size -= 1
                        elif i == 6 and evolver.freq_mut_chance <= 0.98:
                            evolver.freq_mut_chance += 0.02
                            evolver.freq_mut_chance = round(evolver.freq_mut_chance, 2)
                        elif i == 7 and evolver.freq_mut_chance >= 0.02:
                            evolver.freq_mut_chance -= 0.02
                            evolver.freq_mut_chance = round(evolver.freq_mut_chance, 2)
                        elif i == 8 and evolver.space_mut_chance <= 0.98:
                            evolver.space_mut_chance += 0.02
                            evolver.space_mut_chance = round(evolver.space_mut_chance, 2)
                        elif i == 9 and evolver.space_mut_chance >= 0.02:
                            evolver.space_mut_chance -= 0.02
                            evolver.space_mut_chance = round(evolver.space_mut_chance, 2)
                        elif i == 10:
                            evolver.freq_mut_factor += 0.02
                            evolver.freq_mut_factor = round(evolver.freq_mut_factor, 2)
                        elif i == 11 and evolver.freq_mut_factor >= 0.02:
                            evolver.freq_mut_factor -= 0.02
                            evolver.freq_mut_factor = round(evolver.freq_mut_factor, 2)
                        elif i == 12:
                            evolver.space_mut_factor += 0.02
                            evolver.space_mut_factor = round(evolver.space_mut_factor, 2)
                        elif i == 13 and evolver.space_mut_factor >= 0.02:
                            evolver.space_mut_factor -= 0.02
                            evolver.space_mut_factor = round(evolver.space_mut_factor, 2)
                        
        elif event.type == pygame.MOUSEBUTTONUP:
            for i in range(len(control_selected)):
                if control_selected[i] and i >= 2:
                    control_selected[i] = False
    
    # Draw
    draw_population_background()
    draw_population()
    draw_controls()
    draw_stats()
    surface = screen.subsurface((0,POP_DOWN_BOUND, music.shape[0], music.shape[1]))
    pygame.surfarray.blit_array(surface, music)
    
    # Update
    pygame.display.update()
