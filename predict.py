import string
import math
import random
from flask import Flask, render_template, request

app = Flask(__name__)

# Load leaked passwords from file
def load_leaked_passwords(filename):
    with open(filename, "r", encoding="utf-8", errors="ignore") as file:
        return set(line.strip() for line in file)

# Load RockYou dataset (or any other leaked password list)
LEAKED_PASSWORDS = load_leaked_passwords("rockyou.txt")

# Function to calculate entropy (higher = stronger)
def calculate_entropy(password):
    char_space = 0
    if any(c.islower() for c in password):
        char_space += 26
    if any(c.isupper() for c in password):
        char_space += 26
    if any(c.isdigit() for c in password):
        char_space += 10
    if any(c in string.punctuation for c in password):
        char_space += len(string.punctuation)
    
    entropy = len(password) * math.log2(char_space) if char_space else 0
    return round(entropy, 2)

# Estimate time-to-crack (approximate brute-force estimate)
def time_to_crack(entropy):
    if entropy < 28:
        return "Instantly"
    elif entropy < 36:
        return "Few seconds"
    elif entropy < 60:
        return "Hours to Days"
    elif entropy < 80:
        return "Years"
    else:
        return "Centuries"

# Strength classification
def classify_strength(password):
    if password in LEAKED_PASSWORDS:
        return "Weak"
    entropy = calculate_entropy(password)
    if entropy < 36:
        return "Weak"
    elif entropy < 60:
        return "Medium"
    else:
        return "Strong"

# Generate a strong random password
def generate_strong_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))

@app.route('/', methods=['GET', 'POST'])
def index():
    suggested_password = generate_strong_password()  # Generate strong password
    
    if request.method == 'POST':
        password = request.form['password']
        entropy = calculate_entropy(password)
        crack_time = time_to_crack(entropy)
        leaked = password in LEAKED_PASSWORDS
        strength = classify_strength(password)
        
        return render_template('index.html', password=password, entropy=entropy, 
                               crack_time=crack_time, leaked=leaked, strength=strength,
                               suggested_password=suggested_password)
    
    return render_template('index.html', suggested_password=suggested_password)

if __name__ == '__main__':
    app.run(debug=True)
