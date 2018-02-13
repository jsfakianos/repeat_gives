Summary

	The code is written in Python 3. The code receives a record of reported donations to political candidates and sorts them into a new record allowing the user to better understand the source of donors with respect to location of the donor, year of donation, and amounts of donations made. Further, the output provides a running total and percentile donation for each zip code for each recipient organization. 


Running

	Running the code can be achieved by copying a record, conforming to the Federal Election Commission's (FEC) defined dictionary, into the input folder of the root directory and name that file 'itcont.txt'. In addition, the user can modify the desired percentile from which the nearest-rank donation is reported by modifying the content of the 'percentile.txt' file in the same folder. A bash file, 'run.sh', file is included in the root directory. Executing run.sh will allow the program to generate the analysis and create a report in 'output/repeating_donors.txt'.


Dependencies

	Three packages are imported;
		1. sys ---> This module provides access to some variables used or maintained by the interpreter and to functions that interact strongly with the interpreter. It is always available.
		2. os ---> This module provides a portable way of using operating system dependent functionality. It is always available.
		3. NumPy ---> NumPy is the fundamental package for scientific computing with Python. (https://docs.scipy.org/doc/numpy-dev/index.html)
