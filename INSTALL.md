# Installation instructions

## Python libraries
Make sure python3 installed. Then install the python libraries.
```bash
pip3 install random pandas sympy pylatex re antlr4-python3-runtime 
```


## LaTeX libraries
Also make sure you have all the required LaTex libraries. An example is the CTAN library `xlop` which is used to render the empty long division tables for students. Depending on the language configured (standard is Dutch), you might need to download the appropriate `babel` packages.

After installation, the packages are loaded through the stylesheets in the `build` folder where the `.tex` is also compiled into a `.pdf`.
