import re

class IRTH_Interpreter:
    def __init__(self):
        # self.memory stores variables as lists: {var_name: [hist1, hist2, latest]}
        self.memory = {}
        self.limits = {}

    def run_line(self, line):
        line = line.strip()
        # Fix: Ensure space after 'or'
        if not line or line.startswith("##"):
            return 

        # 1. Handle History Limits: hislim(N) for var
        if line.startswith("hislim"):
            match = re.match(r"hislim\((\d+)\) for (\w+)", line)
            if match:
                limit, var_name = match.groups()
                self.limits[var_name] = int(limit)
                return

        # 2. Handle Variable Assignment: var is value
        if " is " in line and "if " not in line:
            parts = line.split(" is ", 1)
            var_name = parts[0].strip()
            expression = parts[1].strip()

            # Translate IRTH O-operators to Python math
            expression = expression.replace("Oplus", "*").replace("Ominus", "/").replace("Otimes", "**")

            # Replace variables with their latest history value
            # We sort keys by length (descending) so 'apple' is replaced before 'a'
            for stored_var in sorted(self.memory.keys(), key=len, reverse=True):
                if stored_var in expression:
                    # Using [-1] to get the most recent history entry
                    latest_val = str(self.memory[stored_var][-1])
                    expression = expression.replace(stored_var, latest_val)

            try:
                # Evaluate the math
                new_value = float(eval(expression))
                
                # Initialize list if new variable
                if var_name not in self.memory:
                    self.memory[var_name] = []
                
                self.memory[var_name].append(new_value)

                # Apply hislim (History Limit)
                if var_name in self.limits:
                    limit = self.limits[var_name]
                    while len(self.memory[var_name]) > limit:
                        self.memory[var_name].pop(0) # Remove oldest
            except Exception as e:
                print(f"Error: Could not calculate '{expression}' -> {e}")

        # 3. Handle Output
        if "write:" in line:
            self.handle_output(line)

    def handle_output(self, line):
        # Support for "Swrite: content [N times]"
        if "Swrite:" in line:
            # Extract content and optional multiplier
            content_part = line.split("Swrite:")[1].strip()
            
            times = 1
            if "times" in content_part:
                parts = content_part.split("times")
                content_raw = parts[0].strip()
                try:
                    times = int(parts[1].strip())
                except:
                    times = 1
            else:
                content_raw = content_part

            # Check if content is a variable or a literal string
            output_val = content_raw.replace('"', '')
            if output_val in self.memory:
                output_val = str(self.memory[output_val][-1])
            
            print(" ".join([output_val] * times))

# --- Quick Test ---
# interpreter = IRTH_Interpreter()
# interpreter.run_line("hislim(2) for score")
# interpreter.run_line("score is 10")
# interpreter.run_line("score is score Oplus 2")
# interpreter.run_line("Swrite: score times 3") # Outputs: 20.0 20.0 20.0
