
This folder contains excell files one for every plc
the excell file can contain:

		-the information to connect to a plc (ip adress, rack , slot) 		(must)
		-info of the db with all int variables (type , adress , value , ...) 	(option)
		-a list of every inputs							(option)		
		-a list of every outpus							(option)

When the program initiate an instance of the class PLC
It read the data from that excell file
that data is necesery to make an connection and read and write to the PLC

It's important to write all the info as a text format
	(right mouse click over all the fields -> Format Cells -> category : TEXT )

the data should me written as followed:

	(watch out for spaces and lower and uppercase)

sheets:
	info_PLC:	this sheet contains all the info for connecting to a plc
	Inputs:		this sheet contains all io inputs
	Outputs:	this sheet contains all io outputs
	DB.:		this sheet contains all the variables of the db


	note: info_plc is the only sheet that is a must the other sheets are options

	info_PLC:
		sheetname = "info_PLC"

		A		|	B   (this colum needs to be filled in examples underneed)
	-------------------------------------------
	1|	IP_adress	|	10.32.0.95
	2|	rack		|	0
	3|	slot		|	2



	DB:
		sheetname = "DB{number}"	(example DB5)

		A	|	B	|	C		|	D		|	E
	---------------------------------------------------------------------------------------
	1|	adress	|	Name	|	Type		|	Initial Value	|	Comment	
	2|		|		|	STRUCT		|			|

					begin variables

	3|	0.0	|	first	|	BOOL		|	FALSE		|	the first boolean
	4|	0.1	|	second	|	BOOL		|	TRUE		|	the second boolean
	5|	2.0	|	big	|	DINT		|	260		|
	6|	6.0	|	div	|	REAL		|	15.3		|	No comment

					.
					.
					.
	
	100|	250.0	|	last	|	DATE		|	D#1991-5-30	|	the best day ever
					end variables
	101|	252.0	|		|	ENDSTRUCT	|			|

	
	note: 	the variables can be copied and pasted from simatic manager. 
		Make sure that the adress are filled in, as wel is the first two and last row.



















