import random

def z_d():
    # Assuming 100 staff members
    staff_ids = [f"staff_id_{i}" for i in range(1, 101)]

    # Variables named 'v1' to 'v100'
    variables = [f"v{i}" for i in range(1, 10)]

    # Creating domains: for each variable, assign a random subset of staff_ids
    domains = {var: random.sample(staff_ids, random.randint(1, 20)) for var in variables}

    return (variables, domains)

def FC_2(UNLABELLED, D, C, compound_label, assignment):
    if not UNLABELLED:
        return assignment  # Return the result when all variables are assigned

    else:
        x = UNLABELLED.pop()
        for v in D[x]:
            assignment[x] = v
            D_prime = Update_2(UNLABELLED - {x}, D, C, compound_label, assignment, x, v)

            if all(D_prime[y] for y in D_prime):
                result = FC_2(UNLABELLED - {x}, D_prime, C, compound_label, assignment)
                if result is not None:
                    return result

            assignment[x] = -1  # Reset the assigned value if a solution was not found

        return None

def Update_2(W, D, C, compound_label, assignment, x, v):
    D_prime = D.copy()

    for y in W:
        for val in D_prime[y][:]:
            if not is_compatible(y, val, compound_label, C, assignment):
                D_prime[y].remove(val)

    return D_prime

def is_compatible(y, val, compound_label, C, assignment):
    # Implement the compatibility check based on your specific constraints here
    # Return True if <y, val> is compatible with compound_label with respect to constraints on y and variables of compound_label
    c1 = True
    c2 = True
    c3 = True
    c4 = False
    c5 = False
    # result =  (c1 and c2 and c3 or c4 or c5)
        # List with 90% True and 10% False
    choices = [True] * 9 + [False]

    # Randomly choose from the list
    result = random.choice(choices)
    # result = random.choice([True, False])
    return result
    #or constraints represent the soft constraints and should be saved for feedback when false returned

def run_iterations(iteration, max_iterations):
    variables, domains = z_d()
    C = {}  # Constraints
    compound_label = [-1, -1, -1]  # Initial compound label (initialize with -1 values)
    UNLABELLED = set(variables)
    assignment = {}  # Reset assignment on each iteration

    solution = FC_2(UNLABELLED, domains, C, compound_label, assignment)

    if solution is not None:
        print("Solution found:", solution)
        print(f'*******************Pass{iteration}*******************')
    else:
        print(f"No solution found in iteration {iteration + 1}")

    if iteration < max_iterations - 1:  # Set the maximum number of iterations
        run_iterations(iteration + 1, max_iterations)  # Recursive call for the next iteration
    else:
        print("Max iterations reached. Exiting the program.")  # Exit if max_iterations is reached

# Start the iterations
run_iterations(0, 100)  # Start with iteration 0