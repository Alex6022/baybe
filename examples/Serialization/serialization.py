### Example for the serialization of a BayBE object

"""
This example shows how to serialize and also de-serialize a BayBE object.
It demonstrates and shows that the "original" and "new" objects behave the same.
"""

# This example assumes some basic familiarity with using BayBE.
# We thus refer to [`baybe_object`](./../Basics/baybe_object.md) for a basic example.

#### Necessary imports

import numpy as np

from baybe.core import BayBE
from baybe.parameters import Categorical, GenericSubstance, NumericDiscrete
from baybe.searchspace import SearchSpace
from baybe.strategies.bayesian import SequentialGreedyRecommender
from baybe.strategies.sampling import FPSRecommender
from baybe.strategies.strategy import Strategy
from baybe.targets import NumericalTarget, Objective

### Experiment setup

parameters = [
    Categorical(
        name="Granularity",
        values=["coarse", "medium", "fine"],
        encoding="OHE",
    ),
    NumericDiscrete(
        name="Pressure[bar]",
        values=[1, 5, 10],
        tolerance=0.2,
    ),
    NumericDiscrete(
        name="Temperature[degree_C]",
        values=np.linspace(100, 200, 10),
    ),
    GenericSubstance(
        name="Solvent",
        data={
            "Solvent A": "COC",
            "Solvent B": "CCC",
            "Solvent C": "O",
            "Solvent D": "CS(=O)C",
        },
        encoding="MORDRED",
    ),
]

### Creating the BayBE object

baybe_orig = BayBE(
    searchspace=SearchSpace.from_product(parameters=parameters, constraints=None),
    objective=Objective(
        mode="SINGLE", targets=[NumericalTarget(name="Yield", mode="MAX")]
    ),
    strategy=Strategy(
        recommender=SequentialGreedyRecommender(),
        initial_recommender=FPSRecommender(),
    ),
)

### Serialization and de-serialization

# We begin by printing the original BayBE object
print(f"{'#'*30} Original object {'#'*30}")
print(baybe_orig, end="\n" * 3)

# We next serialize the BayBE object to JSON.
# This yields a JSON representation  in string format.
# Since it is rather complex, we do not print this string here.
string = baybe_orig.to_json()
print(f"{'#'*30} JSON string {'#'*30}")


# Deserialize the JSON string back to an object.
print(f"{'#'*30} Deserialized object {'#'*30}")
baybe_recreate = BayBE.from_json(string)
print(baybe_recreate, end="\n" * 3)

# Verify that both objects are equal.
assert baybe_orig == baybe_recreate
print("Passed basic assertion check!")

### Comparing recommendations in both objects

# To further show how serialization affects working with BayBE objects, we will now
# create and compare some recommendations in both bayBE objects.

recommendation_orig = baybe_orig.recommend(batch_quantity=2)
recommendation_recreate = baybe_recreate.recommend(batch_quantity=2)

print("Recommendation from original object:")
print(recommendation_orig)

print("Recommendation from recreated object:")
print(recommendation_recreate)
