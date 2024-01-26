def get_cell(pos, titanic_pos, iceberg_pos):
    if pos == titanic_pos:
        return '🚢'
    if pos == iceberg_pos:
        return '🧊'
    return '🟦'

def auto_pilot_next_step(titanic_pos, ocean_size, iceberg_pos):
    if titanic_pos[1] > 0:
        return 'WEST'  
    else:
        return 'REACHED_WEST'  

def simulate_titanic_voyage(initial_titanic_pos, initial_iceberg_pos, ocean_size):
    while True:
        next_step = auto_pilot_next_step(initial_titanic_pos, ocean_size, initial_iceberg_pos)

        if next_step == 'REACHED_WEST':
            print("Titanic has reached the west side.")
            break

        if next_step == 'WEST':
            initial_titanic_pos[1] -= 1

        for i in range(ocean_size):
            for j in range(ocean_size):
                pos = [i, j]
                cell = get_cell(pos, initial_titanic_pos, initial_iceberg_pos)
                print(cell, end=" ")
            print()

# Change Titanic's starting position and iceberg's starting position here:
initial_titanic_pos = [5, 8]
initial_iceberg_pos = [5, 2]
ocean_size = 10

# Call the simulation function
simulate_titanic_voyage(initial_titanic_pos, initial_iceberg_pos, ocean_size)
