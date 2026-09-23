from option_a_fitness.data_generator import generate_fitness_data


def load_scenario(name):
    return generate_fitness_data(
        scenario=name,
        seed=42,
        number_of_windows=12
    )