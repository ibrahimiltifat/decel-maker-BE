from flask import Flask
from flask import Response
from ortools.linear_solver import pywraplp
import json
from flask import request
from flask import jsonify
from flask_cors import CORS,cross_origin

app=Flask(__name__)

CORS(app)

@app.route("/") 
def test():
    return jsonify(input)   

# @app.route("/username", methods=['POST'])
# def login():
#     input = json.loads(request.data) # or request.form["username"]
#     return jsonify(input) # from flask import jsonify 

# @app.route('/username', methods = ['GET','POST'])
# def members():
#         user=json.loads(request.data)
#         arr=[]
#         arr.append(user["weights"])
#         test=[1,2,3]
#         return jsonify(arr)

@app.route('/username', methods = ['GET','POST'])
def members():
    @cross_origin()
    def isSubsetSum(sset, n, ssum):

        # Base Cases
        if (ssum == 0):
            return []
        # not found
        if (n == 0 and ssum != 0):
            return None

        # If last element is greater than sum, then ignore it
        if (sset[n - 1] > ssum):
            return isSubsetSum(sset, n - 1, ssum);

        # else, check if sum can be obtained by any of the following
        # (a) including the last element
        # (b) excluding the last element
        a1 = isSubsetSum(sset, n - 1, ssum)

        # (b) excluding last element fails
        if a1 is None:
            a2 = isSubsetSum(sset, n - 1, ssum - sset[n - 1])

            # (a) including last element fails
            if a2 is None:
                return None

            # (a) including last element successes
            else:
                return a2 + [sset[n - 1]]
        else:
            return a1

    bool = True
    bins = []
    user=json.loads(request.data)
    weights=user["weights"]
    # weights = [38,28,38,37,37,30,37,37,42,37,31,36,36,36,42,29,29,36,34,39,39,24,39,39,38,26,38,38,35,35,22,42,40,40,20,40,34,36,36,25,25,35,35,22,25,25,35,34,23,25,25,34,34,34,20,20,33,33,33,23,20,33,33,32,22,22,32,32,32,23,23,32,32,31,20,27,31,31,31,20,29,31,30,30,24,27,30,30,30,29,23,28,28,28,28,28,22,23,24,26,27,20,26,26,26,26,38,27,27,27,24,37,24,24,24,24,24,22,23,23,23,23,25,25,31,32,33,42]
    ssum = user["dSize"]
    # n = len(sset)

    while (bool):
        n = len(weights)
        subset = isSubsetSum(weights, n, ssum)
        if subset is not None:
            bins.append(subset)
            for i in subset:
                weights.remove(i)
        else:
            bool = False
            break

    def create_data_model():
        """Create the data for the example."""
        data = {}
        # weights = [38,28,38,37,37,30,37,37,42,37,31,36,36,36,42,29,29,36,34,39,39,24,39,39,38,26,38,38,35,35,22,42,40,40,20,40,34,36,36,25,25,35,35,22,25,25,35,34,23,25,25,34,34,34,20,20,33,33,33,23,20,33,33,32,22,22,32,32,32,23,23,32,32,31,20,27,31,31,31,20,29,31,30,30,24,27,30,30,30,29,23,28,28,28,28,28,22,23,24,26,27,20,26,26,26,26,38,27,27,27,24,37,24,24,24,24,24,22,23,23,23,23,25,25,31,32,33,42]
        data['weights'] = weights
        data['items'] = list(range(len(weights)))
        data['bins'] = data['items']
        data['bin_capacity'] = ssum
        return data

    data = create_data_model()

    # Create the mip solver with the SCIP backend.
    solver = pywraplp.Solver.CreateSolver('SCIP')

    # Variables
    # x[i, j] = 1 if item i is packed in bin j.
    x = {}
    for i in data['items']:
        for j in data['bins']:
            x[(i, j)] = solver.IntVar(0, 1, 'x_%i_%i' % (i, j))

    # y[j] = 1 if bin j is used.
    y = {}
    for j in data['bins']:
        y[j] = solver.IntVar(0, 1, 'y[%i]' % j)

    # Constraints
    # Each item must be in exactly one bin.
    for i in data['items']:
        solver.Add(sum(x[i, j] for j in data['bins']) == 1)

    # The amount packed in each bin cannot exceed its capacity.
    for j in data['bins']:
        solver.Add(
            sum(x[(i, j)] * data['weights'][i] for i in data['items']) <= y[j] *
            data['bin_capacity'])

    # Objective: minimize the number of bins used.
    solver.Minimize(solver.Sum([y[j] for j in data['bins']]))

    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        num_bins = 0.
        for j in data['bins']:
            if y[j].solution_value() == 1:
                bin_items = []
                bin_weight = 0
                for i in data['items']:
                    if x[i, j].solution_value() > 0:
                        bin_items.append(data['weights'][i])

                        bin_weight += data['weights'][i]
                if bin_weight > 0:
                    num_bins += 1
                    # print('Bin number', j)
                    # print('  Items packed:', bin_items)
                    bins.append(bin_items)
                    # print('  Total weight:', bin_weight)
                    # print()
        # print()
        # print('Number of bins used:', num_bins)
        # print('Time = ', solver.WallTime(), ' milliseconds')
    else:
        print('The problem does not have an optimal solution.')

    # print(bins)
    return jsonify(bins)

if __name__=="__main__":
    app.run(debug=True)