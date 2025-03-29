import string
import math
import random
from flask import Flask, render_template, request

app = Flask(__name__)

# Load leaked passwords from file
def load_leaked_passwords(filename):
    try:
        with open(filename, "r", encoding="utf-8", errors="ignore") as file:
            return set(line.strip() for line in file)
    except FileNotFoundError:
        print("Warning: rockyou.txt not found. Leaked password checking will be disabled.")
        return set()

LEAKED_PASSWORDS = load_leaked_passwords("rockyou.txt")

# Function to calculate entropy
def calculate_entropy(password):
    if not password:
        return 0

    char_space = sum(26 for condition in [any(c.islower() for c in password), any(c.isupper() for c in password)])
    char_space += 10 if any(c.isdigit() for c in password) else 0
    char_space += len(string.punctuation) if any(c in string.punctuation for c in password) else 0

    entropy = len(password) * math.log2(char_space) if char_space else 0
    return round(entropy, 2)

# Estimate time-to-crack
def time_to_crack(entropy):
    thresholds = [
        (28, "Instantly"),
        (36, "Few seconds"),
        (60, "Hours to Days"),
        (80, "Years"),
    ]
    for threshold, time in thresholds:
        if entropy < threshold:
            return time
    return "Centuries"

# Classify strength
def classify_strength(password):
    if password in LEAKED_PASSWORDS:
        return "Very Weak"
    
    entropy = calculate_entropy(password)
    return "Weak" if entropy < 36 else "Medium" if entropy < 60 else "Strong"

# User-friendly password generator
def generate_password(length=12, use_symbols=True, use_passphrase=False, complexity="mix"):
    words = ["Blue", "Tiger", "Secure", "Fast", "Strong", "Lion", "Eagle", "Safe"]

    if use_passphrase:
        return f"{random.choice(words)}{random.randint(10,99)}{random.choice(string.punctuation)}"

    numbers = "0123456789"
    letters = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    symbols = "!@#$%^&*"

    if complexity == "numbers":
        return "".join(random.choices(numbers, k=length))
    
    if complexity == "words":
        return "".join(random.choices(words, k=max(1, length // 4)))[:length]

    # Default: Mix of letters, numbers, and symbols
    password = [random.choice(letters.upper())]
    password += random.choices(letters.lower(), k=max(4, length - 6))
    password += random.choices(numbers, k=2)

    if use_symbols:
        password += random.choices(symbols, k=2)

    random.shuffle(password)
    return "".join(password[:length])

@app.route('/', methods=['GET', 'POST'])
def index():
    password_length = int(request.form.get('length', 12))
    use_symbols = request.form.get('symbols') == "on"
    use_passphrase = request.form.get('passphrase') == "on"
    complexity = request.form.get('complexity', 'mix')

    suggested_password = generate_password(
        length=password_length, 
        use_symbols=use_symbols, 
        use_passphrase=use_passphrase,
        complexity=complexity
    )

    if request.method == 'POST':
        password = request.form.get('password', '')

        if not password:  # Prevent empty password crash
            return render_template('index.html', error="Please enter a password.", 
                                   suggested_password=suggested_password, length=password_length, 
                                   symbols=use_symbols, passphrase=use_passphrase, complexity=complexity)

        entropy = calculate_entropy(password)
        crack_time = time_to_crack(entropy)
        leaked = password in LEAKED_PASSWORDS
        strength = classify_strength(password)
        
        return render_template('index.html', password=password, entropy=entropy, 
                               crack_time=crack_time, leaked=leaked, strength=strength,
                               suggested_password=suggested_password, 
                               length=password_length, symbols=use_symbols, passphrase=use_passphrase,
                               complexity=complexity)
    
    return render_template('index.html', suggested_password=suggested_password, 
                           length=password_length, symbols=use_symbols, passphrase=use_passphrase,
                           complexity=complexity)

if __name__ == '__main__':
    app.run(debug=True)
