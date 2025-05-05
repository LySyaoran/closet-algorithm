from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from closetPlus import getDataProcessed_csv, find_closedFrequent_patterns_bottomUp, generate_association_rules
from closetPlus import FPTree as fp

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return 'Hello from Flask on Render!'

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files or 'minsup' not in request.form:
        return jsonify({'error': 'Missing file or minsup'}), 400

    file = request.files['file']
    print(file)
    minsup = request.form['minsup']
    print(minsup)

    if not file or not minsup:
        return jsonify({'error': 'File or minsup is empty'}), 400

    try:
        minsup = float(minsup)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        transactions = getDataProcessed_csv(filepath)
        print("Kết quả từ hàm getDataProcessed_csv:", transactions)

        results, tree= find_closedFrequent_patterns_bottomUp(transactions, minsup)
        print("Kết quả từ hàm find_closedFrequent_patterns_bottomUp:", results)

        if tree is None:
            output_tree = []
        else:
            output_tree = fp.fp_tree_to_dict(tree)

        if results is None:
            output_results = []
        else:
            output_results = [{'pattern': list(k), 'support': v} for k, v in results.items()]

        if results is None:
            output_rules = []
        else:
            output_rules = generate_association_rules(frequent_itemsets_dict=results, transactions=transactions, min_confidence=0.5)

        return jsonify({
            'patterns': output_results,
            'association_rules': output_rules,
            'tree': output_tree
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {e}'}), 500

if __name__ == '__main__':
    app.run(debug=True)