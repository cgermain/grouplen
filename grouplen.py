import re
import os
import sys
import argparse
import csv

FASTA_REGEX = ">(\\S+)(.*\\s)([^>]*)"

parser = argparse.ArgumentParser(description="Combines group data from GPM with sequence length from FASTA files.")
parser.add_argument('group_filename', action="store", help="Path to an excel file of the group info from GPM.")
parser.add_argument('fasta_filenames', action="store", help="One or more FASTA files you want to extract sequence lengths from", nargs="+")

def make_output_filename(filename):
	path = os.path.abspath(filename)
	directory = os.path.split(path)[0]
	full_filename = os.path.split(path)[1]
	base = os.path.splitext(full_filename)[0]
	extension = os.path.splitext(full_filename)[1]
	return os.path.join(directory, base+"_lenghts.csv")

def main():
	arguments = parser.parse_args()
	if not os.path.isfile(arguments.group_filename) :
		print("Error: Check that the group spreadsheet file path is correct")
		return

	for filename in arguments.fasta_filenames:
		if not os.path.isfile(filename):
			print("Error: Check that the FASTA file paths are correct")
			return

	output_filename = make_output_filename(arguments.group_filename)
	regex = re.compile(FASTA_REGEX)
	sequence_lengths = {}

	#Run through all the fasta files and append sequences and lengths to the dictionary
	for fasta_filename in arguments.fasta_filenames:
		with open(fasta_filename, "r") as fasta_file:
			sequences = fasta_file.read()
			for sequence in regex.finditer(sequences):
				if sequence.group(1) in sequence_lengths:
					print("Duplicate sequence found when reading FASTA files: " + sequence.group(1))
				else:
					#Remove the newline characters so we're only counting the exact size of the sequence
					sequence_lengths[sequence.group(1)] = len(sequence.group(3).replace('\n', ''))

	#open the group file and match the ids with the sequeneces in fasta file
	with open(arguments.group_filename, "r") as group_file, open(output_filename, "w+") as output_file:
		csv_reader = csv.reader(group_file, delimiter='\t')
		csv_writer = csv.writer(output_file)

		#skip header in group CSV
		next(csv_reader)
		csv_writer.writerow(["Primary", "Secondary", "Sequence Length"])
		for row in csv_reader:
			primary = row[0]
			primary_id = primary.split(" ")[0]
			#Some groups might not be in the FASTA file such as sp|K2C1_HUMAN|
			if primary_id in sequence_lengths:
				csv_writer.writerow([primary, "", sequence_lengths[primary_id]])
			
			#Run through the remaining secondaries, writing them each out to separate lines
			column = 2
			while column < len(row):
				secondary = row[column]
				secondary_id = row[column].split(" ")[0]
				if secondary_id in sequence_lengths:
					csv_writer.writerow([primary, secondary, sequence_lengths[secondary_id]])
				column+=1

	print("Finished!")
	print("Saved as " + output_filename)

if __name__ == "__main__":
	main()
