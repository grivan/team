import threading,time
from datetime import datetime

blacklisted = ['one','two','three']
positive_words = ['happy','like','amazing','good','love','agree','wonderful','true','enjoyable','great','incredible']
negative_words = ['cry','hate','fuck','kill','die','disgusting','awful','terrible','horrible']

class FuncThread(threading.Thread):
	def __init__(self, target, *args):
		self._target = target
		self._args = args
		threading.Thread.__init__(self)
	def run(self):
		#print "DEBUG: Running thread..."
		self._target(*self._args)

"The Object that represents any request"
class Context(object):
	def __init__(self,string):
		self.string = string
		self.sanitized_string = ''
		self.word_freq_dict = {}
		self.vowel_freq_dict = {}
		self.sentiment = ''
		self.myID = str(id(self))
		self.status = 'in process'
		self.tasks = 0
		self.start_time = ''
		self.end_time = ''
	
	def __str__(self):
		sd = {}
		sd['id']= self.myID
		sd['status']=self.status
		sd['word_freq']=self.word_freq_dict
		sd['vowel_freq']=self.vowel_freq_dict
		sd['completed_tasks']="{0}/4".format(self.tasks)
		sd['sentiment']=self.sentiment
		sd['start_time']=self.start_time
		sd['end_time']=self.end_time
		return "{\n\t"+"\t".join(str(w)+": '"+str(sd[w])+"'\n"for w in sd) + "}"

"Sanitizes the string by removing the blacklisted words, returns sanitized string in lower case"
def sanitize(context):
	context.sanitized_string = ' '.join(w.lower() for w in context.string.split() if w not in blacklisted)

"Computes the freq of words in a sanitized string, returns a dictionary of words in the string with value as frequencies"
def computewordfreq(context):
	#time.sleep(5)
	word_dict = {}
	for word in context.sanitized_string.split():
		try:
			word_dict[word] +=1
		except:
			word_dict[word] = 1
	context.word_freq_dict = word_dict

"Computes the sentiment of the text passed, return 'positve' or 'negative' or 'neutral'"
def computesentiment(context):
	score = 0
	word_dict = context.word_freq_dict
	for word in positive_words:
		if word in word_dict.keys():
			score += word_dict[word]
	for word in negative_words:
		if word in word_dict.keys():
			score -= word_dict[word]
	if(score > 2): context.sentiment = 'positive'
	elif(score < -2): context.sentiment = 'negative'
	else: context.sentiment = 'neutral'

"Computes the vowel frequency in a sanitized string"
def computevowelfreq(context):
	#time.sleep(5)
	vowels = ['a','e','i','o','u']
	vowelfreq_dict = {'a':0,'e':0,'i':0,'o':0,'u':0}
	for letter in context.sanitized_string:
		if(letter in vowels):
				vowelfreq_dict[letter] +=1;
	context.vowel_freq_dict = vowelfreq_dict

"The real meat of the program, run each task as a separate method, takes care of the sequencing"	
def process(context):
	context.start_time = datetime.now()
	sanitize(context)
	context.tasks +=1
	word_freq_thread = FuncThread(computewordfreq,con)
	vowel_freq_thread = FuncThread(computevowelfreq,con)
	sentiment_thread = FuncThread(computesentiment,con)
	vowel_freq_thread.start()
	word_freq_thread.start()
	done_vowel_counting = False
	done_word_counting = False
	done_sentiment = False
	
	while(True):
		if not word_freq_thread.isAlive() and not done_word_counting:
			context.tasks+=1
			sentiment_thread.start()
			done_word_counting = True

		if not vowel_freq_thread.isAlive() and not done_vowel_counting:
			done_vowel_counting = True
			context.tasks+=1
		
		if done_word_counting and not sentiment_thread.isAlive() and not done_sentiment:
			done_sentiment = True
			context.tasks+=1			
	
		if done_vowel_counting and done_word_counting and done_sentiment:
			context.status = 'completed'
			context.end_time = datetime.now()
			break
		

if __name__ == '__main__':	
	#con = Context("Hello! I am just two three posting one status update I like it and I am Happy about it amazing");
	tasks = {}
	
	while(True):
		input = raw_input("Enter Request: GET(G) or POST(P) : ")
		if(input == 'P'):
			string = raw_input("Enter Payload String: ")
			con = Context(string)
			tasks[con.myID] = con
			process_thread = FuncThread(process,con)
			process_thread.start()
			print con.myID
		elif(input == 'G'):
			string = raw_input("Enter ID to GET: ")
			try:
				print tasks[string]
			except:
				print "Invalid ID"

