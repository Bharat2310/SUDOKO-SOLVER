from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from solver import solve_sudoku, validate_board
import copy
import os

app = Flask(__name__, static_folder='static')
CORS(app)  # Enable CORS for frontend-backend communication


@app.route('/solve', methods=['POST'])
def solve():
    """
    Endpoint to solve a Sudoku puzzle.
    
    Expected JSON format:
    {
        "board": [
            [5,3,0,0,7,0,0,0,0],
            [6,0,0,1,9,5,0,0,0],
            ...
        ]
    }
    
    Returns:
    {
        "success": true/false,
        "original": [...],
        "solution": [...],
        "message": "..."
    }
    """
    try:
        # Get JSON data
        data = request.get_json()
        
        if not data or 'board' not in data:
            return jsonify({
                'success': False,
                'message': 'Missing "board" in request body'
            }), 400
        
        board = data['board']
        
        # Validate board format
        is_valid, error_msg = validate_board(board)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': f'Invalid board: {error_msg}'
            }), 400
        
        # Keep original for response
        original_board = copy.deepcopy(board)
        
        # Solve the puzzle
        if solve_sudoku(board):
            return jsonify({
                'success': True,
                'original': original_board,
                'solution': board,
                'message': 'Puzzle solved successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'original': original_board,
                'message': 'No solution exists for this puzzle'
            }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'Sudoku Solver API'
    }), 200


@app.route('/', methods=['GET'])
def home():
    """Serve the frontend HTML."""
    return send_from_directory('static', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory('static', path)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)