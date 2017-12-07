import csv
import sys
import itertools

movies = {} 	#movie dict based on epoch settings key=movie_name, value=actors_list
casts = {}  	#actors dict based on epoch settings key=actor_name, value=movie_list
spfdict = {} 	#minimum distcnace from Kevin Bacon key=actor/movie_name, value=distance
year_movies = {}#movie dict per year key=year,value=movie_list
all_movies = {} #all movies dict read from file key=movie_name, value=actor_list
all_casts = {}	#all actors dict read from file key=actor_name, value=movie_list

start_year = 1800	#start year from SET EPOCH
end_year = 2018		#end year from SET EPOCH

kevin = 'Bacon, Kevin'
true = 1
false = 0 

debug = false

#debug functions
def dump_movies():
	if(debug):
		print('...MOVIES...')
		for key, value in movies.items():
			print(key,value)
		print('............')

def dump_allmovies():
	if(debug):
		print('...ALL MOVIES...')
		for key, value in all_movies.items():
			print(key,value)
		print('............')

def dump_actors():
	if(debug):
		print('...ACTORS...')
		for key, value in casts.items():
			print(key,value)
		print('............')

def dump_spf():
	if(debug):
		print('...SPF...')
		for key, value in spfdict.items():
			print(key,value)
		print('............')

def dump_sortedlist():
	if(debug):
		print('...SORTED LIST...')
		keylist = year_movies.keys()
		keylist.sort()
		for key, value in year_movies.items():
			print(key,value)
		print('............')

def dump_command_list():
	print('Command List...')
	print('COUNT "<movie_name|actor_name>"')
	print('BACON "<movie_name|actor_name>"')
	print('INTERSECT "<movie_name|actor_name>" "<movie_name|actor_name>"')
	print('SET EPOCH <start_year> <end_year>')
	print('UNSET EPOCH')
	print('END')

#Read movie db file into movie and actors dictionary
with open('imdb-movies.txt', 'r') as f:
	sys.setrecursionlimit(8000)

	for line in f:
		#clean up white space and tokenize
		words = line.rstrip('\n').split("/")
		movie_name, year = words[0].split("(");
		movie_year = year.rstrip(')')
		movie_year = year[:4]
		movie_name = movie_name.strip()
		all_movies[movie_name] = words[1:]
		movies_in_year = [movie_name]
		if(movie_year not in year_movies):
			year_movies[movie_year] = movies_in_year
		else:
			year_movies[movie_year].append(movie_name) 
			
		for word in words[1:]:
			if(word not in all_casts):
				a =  [movie_name]
				all_casts[word] = a
			else:
				all_casts[word].append(movie_name)

#Initially set working movie and actors dict
movies = dict(all_movies)
casts = dict(all_casts)
	
#Rebuild working movie and actors dict based on epoch settings
def rebuild_database():
	global movies
	global casts

 	movies.clear()
	casts.clear()

	dump_allmovies()
	dump_movies()
	# Clear database
	keylist = year_movies.keys()
	keylist.sort()
	for key in keylist:
		if((key >= start_year) and (key <= end_year)):
			m_list = year_movies[key]
			for m in m_list:
				if(m not in movies):
					a_list = all_movies[m]
					movies[m] = a_list
				
	for movie in movies:
		artists_list = movies[movie]
		for actor in artists_list:
			if(actor not in casts):
				a = [movie]
				casts[actor] = a
			else:		
				casts[actor].append(movie)

def set_distance(a_list, dist):
	for a in a_list:
		if(a not in spfdict):
			spfdict[a] = dist
		elif(spfdict[a] > dist):
			spfdict[a] = dist
			
		

#Calculate distance from an artist. Uses recursion.
def calculate_distance(artist, rel_num):
	
	if(artist not in casts):
		return

	movie_list = casts[artist]
	if(artist not in spfdict):
		spfdict[artist] = rel_num
	
	#set distance for movie list
	set_distance(movie_list, rel_num)
	
	new_list = []
	#find associated actors
	for movie in movie_list:
		artists_list = movies[movie]
		for actor in artists_list:
			if(actor not in spfdict):
				new_list.append(actor)
			elif(spfdict[actor] > rel_num+1):
				spfdict[actor] = rel_num+1
		
	if(len(new_list) == 0):
		return
	
	set_distance(new_list, rel_num+1)

	for new_actor in new_list:
		calculate_distance(new_actor, rel_num+1)


#Initially calculate distance from Kevin Bacon 
calculate_distance(kevin, 0)

dump_movies()
dump_actors()
dump_sortedlist()
dump_spf()

print('Welcome to IES IMDb Challenge')
dump_command_list()

while (1):
	command = raw_input("Enter a command :")
	test_arg = command.split(' ')
	arg_list = command.split("\"")
	args = []	

	if((test_arg[0] == "COUNT") or (test_arg[0] == "INTERSECT") or ( test_arg[0] == "BACON")):
		for arg in arg_list:
			str(arg).strip()
			str(arg).rstrip('\"')
			if(arg != '' and arg != ' '):
				args.append(arg)
    	else:
			args = test_arg

	args[0] = args[0].strip()

	if(args[0] == "COUNT"):
		if(len(args) < 2):
			print('Invalid command')
		elif(args[1] in movies):
			print(len(movies[args[1]]))
		elif(args[1] in casts):
			print(len(casts[args[1]]))
		else:
			print('0')
	elif(args[0] == "INTERSECT"):
		if(len(args) < 3):
			print('Invalid command')
		elif(((args[1] in movies) and (args[2] in casts)) or ((args[1] in casts) and (args[2] in movies))):
			print('One argument movie and another actor. Both argument has to be same type')
		elif((args[1] in movies) and (args[2] in movies)):
			#print(set(movies[args[1]]) & set(movies[args[2]]))
			
			if(len(set(movies[args[1]]) & set(movies[args[2]])) > 0):
				for m in (set(movies[args[1]]) & set(movies[args[2]])):
					print(m)
			else:
				print('NULL')
		elif((args[1] in casts) and (args[2] in casts)):
			#print(set(casts[args[1]]) & set(casts[args[2]]))
			if(len(set(casts[args[1]]) & set(casts[args[2]])) > 0):
				for c in (set(casts[args[1]]) & set(casts[args[2]])):
					print(c)
			else:
				print('NULL')
		else:
			print('NULL')
	
	elif(args[0] == "BACON"):
		if(len(args) < 2):
			print('Invalid command')
		elif(args[1] == kevin):
			print('0')
		elif(args[1] in spfdict):
			print(spfdict[args[1]])
		else:
			print('INF')

	elif(args[0] == "SET"):
		if(len(args) < 4):
			print('Invalid command')
		elif(args[1] != 'EPOCH'):
			print('Invalid argument')
		else:
			if(args[2] != 'NULL'):
				new_start_year = args[2]
			else:
				new_start_year = '1800'
			if(args[3] != 'NULL'):
				new_end_year = args[3]
			else:
				new_end_year = '2018'
			if((new_start_year == start_year) and (new_end_year == end_year)):
				print('No need to recalculate')
			else:
				start_year = new_start_year
				end_year = new_end_year
				#print('start year, end year', start_year, end_year)
				rebuild_database()
				spfdict.clear()
				dump_spf()
				calculate_distance(kevin, 0)
			dump_movies()
			dump_actors()
			dump_spf()			
	
	elif(args[0] == "UNSET"):
		if(len(args) < 2):
			print('Invalid command')
		if(args[1] == 'EPOCH'):
			new_start_year = '1800' 
			new_end_year = '2018'
			if((new_start_year == start_year) and (new_end_year == end_year)):
				print('No need to recalculate')
			else:
				start_year = new_start_year
				end_year = new_end_year
				#print('start year, end year', start_year, end_year)
				rebuild_database()
				spfdict.clear()
				calculate_distance(kevin, 0)
			dump_movies()
			dump_actors()
			dump_spf()			
		else:
			print('Invalid command')

	elif(args[0] == "END"):
		break

	else:
		print('Enter valid input')

