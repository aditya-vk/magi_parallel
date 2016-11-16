# A sample program to run multiple processes

# Two steps:
# 1. Run the processes continuously
# 2. Kill one process by passing a signal from another


##########################
# Start Preliminary Code #
##########################

# All the processes use the same function and push the result into the same queue. 
# Function is not running continuously.

# Required library
import multiprocessing

# Initalize a Queue that processes can push results into
q = multiprocessing.Queue()

# Define a function for them to use
def square(n,q):
	"""
	n : Number to be squared
	q : queue into which the solution is pushed
	"""
	q.put(n**2)

# Verify the name of the module. To ensure child processes, if any, don't run the following code everytime
if __name__ == '__main__':
	# set up the list of processes to be run. #Processes == #Inputs I am giving. In this case 10.
	processes = [multiprocessing.Process(target = square, args = (x,q)) for x in range(10)]

	# Run the processes
	for p in processes:
		p.start()

	# Exit the completed processes
	for p in processes:
		p.join()

	# Get values from the Queues
	values = [q.get() for p in processes]

	# print the squared values
	print values

########################
# End Preliminary Code #
########################

# Notes from Preliminary: The values from each process is not obtained in order, which is fine for our case.