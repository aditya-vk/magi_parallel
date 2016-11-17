# A sample program to run multiple processes

# ##########################
# # Start Preliminary Code #
# ##########################

# Start both the processes at a certain value, say 0.
# Pause one at 0.1 sec and another at 0.2 sec
# When one of the processes reaches a value say 10, stop the other process and retrieve this queue

import multiprocessing
import time

def slow(q):
	i = 1
	while True:
		q.put(i)
		print i
		i+=1
		time.sleep(0.2)
		if i == 10:
			break

def fast(q):
	i = 1
	while True:
		q.put(i)
		print i
		i+=1
		time.sleep(0.1)
		if i == 10:
			break

if __name__ == '__main__':
	q0 = multiprocessing.Queue()
	q1 = multiprocessing.Queue()

	p0 = multiprocessing.Process(target = slow, args = (q0,))
	p1 = multiprocessing.Process(target = fast, args = (q1,))

	p0.start()
	p1.start()

	p0.join()
	p1.join()
	

	q0.put(-1)
	q1.put(-1)
	v0 = []
	v1 = []

	checker0 = 1
	checker1 = 1

	while checker0 > 0:
		checker0 = q0.get()
		v0.append(checker0)
	while checker1 > 0:
		checker1 = q1.get()
		v1.append(checker1)
	
	print 'values in 1st queue', v0[0:len(v0)-1]
	print 'values in 2nd queue', v1[0:len(v1)-1]



# ########################
# # End Preliminary Code #
# ########################

# Notes from Preliminary: The values from each process is not obtained in order, which is fine for our case.










# import sys
# import select
# import time

# # If there's input ready, do something, else do something
# # else. Note timeout is zero so select won't block at all.
# while True:
# 	while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
# 		line = sys.stdin.readline()
# 		if line:
# 			print 'read: ', line
# 		else: # an empty line means stdin has been closed
# 			print('eof')
# 			time.sleep(3)
# 	    	exit(0)
# 	print 'no input'
# 	time.sleep(1)










#######
# In the following code, PROBLEM is that the queue is getting cleaned in every loop -> Turns out this happens even otherwise
# when the process generates multiple values, only the first one is being stored in the queue. 
#######

# import multiprocessing as mp
# import time
# import sys
# import os
# import select

# def printOne(q,fileno):
#     sys.stdin = os.fdopen(fileno)  #open stdin in this process
#     while True:
#     	# os.system('cls' if os.name == 'nt' else 'clear')
#     	if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
#     		line = raw_input()
#     		break
#         q.put(1)
#         print 1
#         time.sleep(2)


# if __name__ == '__main__':
# 	q0 = mp.Queue()
# 	fn = sys.stdin.fileno()
# 	p = mp.Process(target = printOne,args = (q0,fn))

# 	p.start()
# 	p.join()
# 	values = q0.get()
# 	print 'The queue is made of: ', values