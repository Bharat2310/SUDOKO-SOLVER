from flask import Flask, request, jsonify
from solver import solve_sudoku, validate_board
import copy

app = Flask(__name__)


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
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sudoku Solver</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 600px;
            width: 100%;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 10px;
            font-size: 2em;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 0.9em;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(9, 1fr);
            gap: 0;
            margin: 0 auto 30px;
            width: 100%;
            max-width: 450px;
            border: 3px solid #333;
            background: #333;
        }
        .cell {
            aspect-ratio: 1;
            border: 1px solid #999;
            background: white;
            text-align: center;
            font-size: 1.2em;
            font-weight: 600;
            color: #333;
            outline: none;
            transition: all 0.2s;
        }
        .cell:focus {
            background: #e3f2fd;
            border-color: #667eea;
        }
        .cell.solved {
            background: #e8f5e9;
            color: #2e7d32;
        }
        .cell:nth-child(3n) { border-right: 3px solid #333; }
        .cell:nth-child(n + 19):nth-child(-n + 27),
        .cell:nth-child(n + 46):nth-child(-n + 54) {
            border-bottom: 3px solid #333;
        }
        .buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
        }
        button {
            padding: 12px 30px;
            font-size: 1em;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .solve-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .solve-btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        .clear-btn { background: #f5f5f5; color: #666; }
        .clear-btn:hover { background: #e0e0e0; }
        .example-btn { background: #fff3e0; color: #e65100; }
        .example-btn:hover { background: #ffe0b2; }
        button:disabled { opacity: 0.5; cursor: not-allowed; }
        .status {
            text-align: center;
            margin-top: 20px;
            padding: 15px;
            border-radius: 8px;
            font-weight: 500;
            display: none;
        }
        .status.success { background: #e8f5e9; color: #2e7d32; display: block; }
        .status.error { background: #ffebee; color: #c62828; display: block; }
        .status.loading { background: #e3f2fd; color: #1565c0; display: block; }
        @media (max-width: 500px) {
            .container { padding: 20px; }
            h1 { font-size: 1.5em; }
            .cell { font-size: 1em; }
            button { padding: 10px 20px; font-size: 0.9em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🧩 Sudoku Solver</h1>
        <p class="subtitle">Enter your puzzle and let AI solve it</p>
        <div class="grid" id="grid"></div>
        <div class="buttons">
            <button class="solve-btn" onclick="solvePuzzle()">Solve Puzzle</button>
            <button class="example-btn" onclick="loadExample()">Load Example</button>
            <button class="clear-btn" onclick="clearGrid()">Clear All</button>
        </div>
        <div class="status" id="status"></div>
    </div>
    <script>
        const grid = document.getElementById('grid');
        const status = document.getElementById('status');
        let cells = [];
        
        function initGrid() {
            grid.innerHTML = '';
            cells = [];
            for (let i = 0; i < 81; i++) {
                const input = document.createElement('input');
                input.type = 'text';
                input.className = 'cell';
                input.maxLength = 1;
                input.addEventListener('input', handleInput);
                input.addEventListener('keydown', handleKeydown);
                grid.appendChild(input);
                cells.push(input);
            }
        }
        
        function handleInput(e) {
            const value = e.target.value;
            if (value && (value < '1' || value > '9')) {
                e.target.value = '';
            }
            e.target.classList.remove('solved');
        }
        
        function handleKeydown(e) {
            const index = cells.indexOf(e.target);
            let nextIndex = -1;
            switch(e.key) {
                case 'ArrowUp': nextIndex = index - 9; e.preventDefault(); break;
                case 'ArrowDown': nextIndex = index + 9; e.preventDefault(); break;
                case 'ArrowLeft': nextIndex = index - 1; e.preventDefault(); break;
                case 'ArrowRight': nextIndex = index + 1; e.preventDefault(); break;
            }
            if (nextIndex >= 0 && nextIndex < 81) {
                cells[nextIndex].focus();
            }
        }
        
        function getBoardFromGrid() {
            const board = [];
            for (let i = 0; i < 9; i++) {
                const row = [];
                for (let j = 0; j < 9; j++) {
                    const value = cells[i * 9 + j].value;
                    row.push(value ? parseInt(value) : 0);
                }
                board.push(row);
            }
            return board;
        }
        
        function setBoardToGrid(board, markSolved = false) {
            for (let i = 0; i < 9; i++) {
                for (let j = 0; j < 9; j++) {
                    const cell = cells[i * 9 + j];
                    const value = board[i][j];
                    if (value !== 0) {
                        cell.value = value;
                        if (markSolved) {
                            cell.classList.add('solved');
                        }
                    }
                }
            }
        }
        
        function showStatus(message, type) {
            status.textContent = message;
            status.className = 'status ' + type;
        }
        
        function hideStatus() {
            status.className = 'status';
        }
        
        async function solvePuzzle() {
            const board = getBoardFromGrid();
            const originalBoard = board.map(row => [...row]);
            showStatus('Solving puzzle...', 'loading');
            
            try {
                const response = await fetch('/solve', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ board: board })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    for (let i = 0; i < 9; i++) {
                        for (let j = 0; j < 9; j++) {
                            if (originalBoard[i][j] === 0 && data.solution[i][j] !== 0) {
                                cells[i * 9 + j].classList.add('solved');
                            }
                        }
                    }
                    setBoardToGrid(data.solution, true);
                    showStatus('✓ Puzzle solved successfully!', 'success');
                } else {
                    showStatus('✗ ' + data.message, 'error');
                }
            } catch (error) {
                showStatus('✗ Error: Could not solve puzzle', 'error');
                console.error(error);
            }
        }
        
        function clearGrid() {
            cells.forEach(cell => {
                cell.value = '';
                cell.classList.remove('solved');
            });
            hideStatus();
        }
        
        function loadExample() {
            const example = [
                [5,3,0,0,7,0,0,0,0],
                [6,0,0,1,9,5,0,0,0],
                [0,9,8,0,0,0,0,6,0],
                [8,0,0,0,6,0,0,0,3],
                [4,0,0,8,0,3,0,0,1],
                [7,0,0,0,2,0,0,0,6],
                [0,6,0,0,0,0,2,8,0],
                [0,0,0,4,1,9,0,0,5],
                [0,0,0,0,8,0,0,7,9]
            ];
            clearGrid();
            setBoardToGrid(example);
            hideStatus();
        }
        
        initGrid();
    </script>
</body>
</html>'''


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)