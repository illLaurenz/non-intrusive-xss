# SYSTEM SETTINGS
BWAPP_URL = "http://127.0.0.1:4040/"
FLASK_URL = "http://localhost:5000/submit/<id>"
DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "xss"
DB_PASS = "xss"
DB_NAME = "xss_db"
MAX_PROCESS_COUNT = 4

# LOG LEVEL
VERBOSE = True

# GA FACTORS
MUTATION_RATE = 5           # [Natural number] HIGHER -> higher chance of mutated payloads in next gen, which were successful in the current iteration
REPRODUCTION_RATE = 1       # [Natural number] HIGHER -> higher chance of offspring of two successful payloads in the next gen
SUCCESS_FACTOR = 1          # [Natural number] HIGHER -> the best payloads are more likely to mutate and reproduce
SUCCESS_THRESHOLD = 0.2     # [Fraction 0 <= f <= 1] The max percentage of the population size, which is considered successful

IMAGE_DIFF_UPPER_THRESH = 3    # [Fraction > 1] HIGHER -> Images must have more significant differences to be considered different
IMAGE_DIFF_LOWER_THRESH = 2    # [Fraction > Upper thresh] HIGHER -> Images must have more significant differences to be considered slightly different