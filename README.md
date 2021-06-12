# Teaching mathematical operators

## Worksheet generation
This Python script generates different types of arithmetic exercises in LaTeX for math teaching. The result is a `.pdf` file that contains question with enough blank space and answers at the end for the teacher. 

- blank space is computed based on the complexity of the problem
- solutions are always integers
- adding new operators to make new types of questions should be quite easy

For installation instructions, see the file [INSTALL.md](INSTALL.md) in this repository.

## Example usage
To use this library, choose operators that you want to teach in class. For example, to you could decide to build a section that helps students pratice simplifying fractions and computing roots by choosing the `frac_op` and the `sqrt_op` operator. Feed these operators to the arithmetic problem generator to obtain a problem section with these operators in the pdf.

You can edit the sections with the types of questions you would like at the end of `questions.py`. Then  run the file with Python to obtain a `.pdf` file called `doc.pdf` with problems at the beginning and solutions attached at the end.

## Work in progress


Should still be implemented: 
- Storing generated problems in database