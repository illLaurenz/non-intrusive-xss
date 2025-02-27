# SYSTEM SETTINGS
BWAPP_URL = "http://127.0.0.1:4040/"
FLASK_URL = "http://localhost:5000/submit/<id>"
DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "xss"
DB_PASS = "xss"
DB_NAME = "xss_db"
PROCESS_COUNT = 4

# LOG LEVEL
VERBOSE = True

# GA FACTORS
MUTATION_RATE = 3           # HIGHER -> higher chance of mutated payloads in next gen, which were successful in the current iteration
REPRODUCTION_RATE = 1       # HIGHER -> higher chance of offspring of two successful payloads in the next gen
SUCCESS_FACTOR = 2          # HIGHER -> the best payloads are more likely to mutate and reproduce
SUCCESS_THRESHOLD = 0.2     # The max percentage of the population size, which is considered successful

IMAGE_DIFF_THRESHOLD = 4    #