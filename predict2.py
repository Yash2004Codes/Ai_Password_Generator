import string
import math
import random
from flask import Flask, render_template, request

app = Flask(__name__)

# Load leaked passwords from file
def load_leaked_passwords(filename):
    with open(filename, "r", encoding="utf-8", errors="ignore") as file:
        return set(line.strip() for line in file)

LEAKED_PASSWORDS = load_leaked_passwords("rockyou.txt")

# Function to calculate entropy
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

# Estimate time-to-crack
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

# Classify strength
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

# User-friendly password generator
def generate_user_friendly_password(length=12, use_symbols=True, use_passphrase=False):
    words = ["Blue", "Tiger", "Secure", "Fast", "Strong", "Lion", "Eagle", "Safe"]
    
    if use_passphrase:
        return f"{random.choice(words)}{random.randint(10,99)}{random.choice(string.punctuation)}"

    # Avoid confusing characters
    letters = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"  # Removed O, 0, l, 1
    digits = "23456789"  # Removed 0 and 1
    symbols = "!@#$%^&*"

    # Start with an uppercase letter
    password = [random.choice(letters.upper())]

    # Add some lowercase letters
    password += random.choices(letters.lower(), k=max(4, length - 6))  

    # Add some digits
    password += random.choices(digits, k=2)

    # Add symbols if enabled
    if use_symbols:
        password += random.choices(symbols, k=2)

    # Shuffle for randomness
    random.shuffle(password)

    return "".join(password[:length])

@app.route('/', methods=['GET', 'POST'])
def index():
    password_length = int(request.form.get('length', 12))  # Default 12
    use_symbols = request.form.get('symbols') == "on"
    use_passphrase = request.form.get('passphrase') == "on"

    suggested_password = generate_user_friendly_password(
        length=password_length, 
        use_symbols=use_symbols, 
        use_passphrase=use_passphrase
    )

    if request.method == 'POST':
        password = request.form['password']
        entropy = calculate_entropy(password)
        crack_time = time_to_crack(entropy)
        leaked = password in LEAKED_PASSWORDS
        strength = classify_strength(password)
        
        return render_template('index.html', password=password, entropy=entropy, 
                               crack_time=crack_time, leaked=leaked, strength=strength,
                               suggested_password=suggested_password, 
                               length=password_length, symbols=use_symbols, passphrase=use_passphrase)
    
    return render_template('index.html', suggested_password=suggested_password, 
                           length=password_length, symbols=use_symbols, passphrase=use_passphrase)

if __name__ == '__main__':
    app.run(debug=True)
