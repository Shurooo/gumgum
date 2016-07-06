# gumgum

Preprocessor reads files with json objects. For each json object, it takes data fields we are interested in and convert the values into numbers representing the corresonding categories.

Converter reads the output of Preprocessor, and converts the categorical data into columns of binary values that are suitable for machine learning. For example, if a particular feature has 5 categories, an entry like [3] will be converted to [0, 0, 1, 0, 0]
