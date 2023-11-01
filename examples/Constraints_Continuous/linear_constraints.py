### Example for linear constraints in a continuous searchspace
# pylint: disable=missing-module-docstring
import numpy as np

# Example for optimizing a synthetic test functions in a continuous space with linear
# constraints.
# All test functions that are available in BoTorch are also available here and wrapped
# via the `botorch_function_wrapper`.

# This example assumes some basic familiarity with using BayBE.
# We thus refer to [`baybe_object`](./../Basics/baybe_object.md) for a basic example.
# Also, there is a large overlap with other examples with regards to using the test function.
# We thus refer to [`discrete_space`](./discrete_space.md) for details on this aspect.


#### Necessary imports for this example

from baybe import BayBE
from baybe.constraints import (
    ContinuousLinearEqualityConstraint,
    ContinuousLinearInequalityConstraint,
)
from baybe.parameters import NumericalContinuousParameter
from baybe.searchspace import SearchSpace
from baybe.targets import NumericalTarget, Objective
from baybe.utils import botorch_function_wrapper

from botorch.test_functions import Rastrigin

#### Defining the test function

# See [`discrete_space`](./../Searchspaces/discrete_space.md) for details.

DIMENSION = 4
TestFunctionClass = Rastrigin

if not hasattr(TestFunctionClass, "dim"):
    TestFunction = TestFunctionClass(dim=DIMENSION)  # pylint: disable = E1123
else:
    TestFunction = TestFunctionClass()
    DIMENSION = TestFunctionClass().dim

BOUNDS = TestFunction.bounds
WRAPPED_FUNCTION = botorch_function_wrapper(test_function=TestFunction)

#### Creating the searchspace and the objective

# Since the searchspace is continuous test, we construct `NumericalContinuousParameter`s
# We use that data of the test function to deduce bounds and number of parameters.
parameters = [
    NumericalContinuousParameter(
        name=f"x_{k+1}",
        bounds=(BOUNDS[0, k], BOUNDS[1, k]),
    )
    for k in range(DIMENSION)
]

# We model the following constraints:
# `1.0*x_1 + 1.0*x_2 = 1.0`
# `1.0*x_3 - 1.0*x_4 = 2.0`
# `1.0*x_1 + 1.0*x_3 >= 1.0`
# `2.0*x_2 + 3.0*x_4 <= 1.0` which is equivalent to `-2.0*x_2 - 3.0*x_4 >= -1.0`
constraints = [
    ContinuousLinearEqualityConstraint(
        parameters=["x_1", "x_2"], coefficients=[1.0, 1.0], rhs=1.0
    ),
    ContinuousLinearEqualityConstraint(
        parameters=["x_3", "x_4"], coefficients=[1.0, -1.0], rhs=2.0
    ),
    ContinuousLinearInequalityConstraint(
        parameters=["x_1", "x_3"], coefficients=[1.0, 1.0], rhs=1.0
    ),
    ContinuousLinearInequalityConstraint(
        parameters=["x_2", "x_4"], coefficients=[-2.0, -3.0], rhs=-1.0
    ),
]

searchspace = SearchSpace.from_product(parameters=parameters, constraints=constraints)
objective = Objective(
    mode="SINGLE", targets=[NumericalTarget(name="Target", mode="MIN")]
)

#### Construct the BayBE object and run some iterations

baybe_obj = BayBE(
    searchspace=searchspace,
    objective=objective,
)

BATCH_QUANTITY = 3
N_ITERATIONS = 3

for k in range(N_ITERATIONS):
    recommendation = baybe_obj.recommend(batch_quantity=BATCH_QUANTITY)

    # target value are looked up via the botorch wrapper
    target_values = []
    for index, row in recommendation.iterrows():
        target_values.append(WRAPPED_FUNCTION(*row.to_list()))

    recommendation["Target"] = target_values

    baybe_obj.add_measurements(recommendation)

### Verify the constraints
measurements = baybe_obj.measurements_exp
TOLERANCE = 0.01

# `1.0*x_1 + 1.0*x_2 = 1.0`
print(
    "1.0*x_1 + 1.0*x_2 = 1.0 satisfied in all recommendations? ",
    np.allclose(
        1.0 * measurements["x_1"] + 1.0 * measurements["x_2"], 1.0, atol=TOLERANCE
    ),
)

# `1.0*x_3 - 1.0*x_4 = 2.0`
print(
    "1.0*x_3 - 1.0*x_4 = 2.0 satisfied in all recommendations? ",
    np.allclose(
        1.0 * measurements["x_3"] - 1.0 * measurements["x_4"], 2.0, atol=TOLERANCE
    ),
)

# `1.0*x_1 + 1.0*x_3 >= 1.0`
print(
    "1.0*x_1 + 1.0*x_3 >= 1.0 satisfied in all recommendations? ",
    (1.0 * measurements["x_1"] + 1.0 * measurements["x_3"]).ge(1.0 - TOLERANCE).all(),
)

# `2.0*x_2 + 3.0*x_4 <= 1.0`
print(
    "2.0*x_2 + 3.0*x_4 <= 1.0 satisfied in all recommendations? ",
    (2.0 * measurements["x_2"] + 3.0 * measurements["x_4"]).le(1.0 + TOLERANCE).all(),
)