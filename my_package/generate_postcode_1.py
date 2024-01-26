import random

def generate_postcode():
    # List of valid UK postcode areas
    postcode_areas = ["AB", "AL", "B", "BA", "BB", "BD", "BH", "BL", "BN", "BR", "BS", "BT", "CA", "CB", "CF", "CH", "CM", "CO", "CR", "CT", "CV", "CW", "DA", "DD", "DE", "DG", "DH", "DL", "DN", "DT", "DY", "E", "EC", "EH", "EN", "EX", "FK", "FY", "G", "GL", "GU", "HA", "HD", "HG", "HP", "HR", "HS", "HU", "HX", "IG", "IP", "IV", "KA", "KT", "KW", "KY", "L", "LA", "LD", "LE", "LL", "LN", "LS", "LU", "M", "ME", "MK", "ML", "N", "NE", "NG", "NN", "NP", "NR", "NW", "OL", "OX", "PA", "PE", "PH", "PL", "PO", "PR", "RG", "RH", "RM", "S", "SA", "SE", "SG", "SK", "SL", "SM", "SN", "SO", "SP", "SR", "SS", "ST", "SW", "SY", "TA", "TD", "TF", "TN", "TQ", "TR", "TS", "TW", "UB", "W", "WA", "WC", "WD", "WF", "WN", "WR", "WS", "WV", "YO", "ZE"]
    
    # Randomly select a postcode area
    postcode_area = random.choice(postcode_areas)
    
    # Generate a random district within the postcode area
    district = random.randint(0, 99)
    
    # Generate a random sector within the district
    sector = random.randint(1, 9)
    
    # Generate a random unit within the sector
    unit = random.choice(["AA", "AB", "BA", "BB", "CA", "CB", "DA", "DB", "EA", "EB", "FA", "FB", "GA", "GB", "HA", "HB", "JA", "JB", "LA", "LB", "MA", "MB", "NA", "NB", "PA", "PB", "RA", "RB", "SA", "SB", "TA", "TB", "UA", "UB", "VA", "VB", "WA", "WB", "YA", "YB", "ZA", "ZB"])
    
    # Construct the full postcode
    postcode = "{}{} {}{}".format(postcode_area, district, sector, unit)
    
    return postcode


def generate_postcodes(num_postcodes):
    postcodes = []
    for i in range(num_postcodes):
        postcode = generate_postcode()
        postcodes.append(postcode)
    return postcodes

# print(generate_postcodes(100))