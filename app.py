from flask import Flask, request, jsonify
import pandas as pd
import logging

# Initialize the Flask app
app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Define the API route for analysis
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Log the incoming request data
        app.logger.debug(f"Incoming request data: {request.json}")
        
        # Get JSON data from the request
        data = request.json
        
        # Check if data is None or empty
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Convert JSON data to a Pandas DataFrame
        df = pd.DataFrame(data)
        
        # Perform your analysis here
        # Example: Calculate summary statistics
        result = df.describe().to_dict()
        
        # Return the result as JSON
        return jsonify(result)
    
    except Exception as e:
        # Log the error
        app.logger.error(f"Error: {str(e)}")
        # Handle errors
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)