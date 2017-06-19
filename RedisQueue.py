import redis

class RedisQueue(object):
	"""RedisQueue will manage data queuing releted work
	   Here adding RoadConditon and EnvironmentData json objects
	   and removing top most element will be handled

	   List/Queue will be in FIFO Manner
	"""

	def __init__(self,client,queue_name):
		super(RedisQueue, self).__init__()
		self.client = client
		self.queue_name = queue_name

	def add_to_queue(self,data):
		"""Adding JSON object into queue
		"""

		try:
			pipe = self.client.pipeline()
			pipe.rpush(self.queue_name,data)
			pipe.execute()

		except Exception as e:
			return 0

		return 1


	def get_top_of_queue(self):
		"""Get top element of the queue or None if queue is empty
		"""

		try:
                        data = self.client.lpop(self.queue_name)
		except Exception as e:
			return None

		return data


	def get_length_of_queue(self):
		"""Returns Length of the queue
		   or 0 if empty or not-exist
		"""
		length = 0
		try:
			length = self.client.llen(self.queue_name)
			
		except Exception as e:
			return 0

		return length
