#God is a singleton that stores configuration and prints daily summaries
class God(object):
	__instance = None
	def __new__(cls):
		if God.__instance is None:
			God.__instance = object.__new__(cls)
		return God.__instance
	
	def __init__(self):
		self._defaults = {"c_term_mutate_rate": 10, "c_coeff_mutate_rate": 70, "c_term_loss_rate": 5, "c_term_merge_rate": 5, "c_no_mutate_rate": 10, "c_message_level": 5, "c_max_solvers": 10,
						  "c_avg_terms": 5, "c_stdev_terms": 1, "c_max_terms": 10}
		

	def loadConfig(self, config = {}):
		self._config = config
		#load defaults if not provided
		if "c_term_mutate_rate" not in self._config:
			self._config["c_term_mutate_rate"] = self._defaults["c_term_mutate_rate"] #rate at which an entire base equation term is changed
		if "c_coeff_mutate_rate" not in self._config:
			self._config["c_coeff_mutate_rate"] = self._defaults["c_coeff_mutate_rate"] #rate at which a coefficient of a base equation term is changed
		if "c_term_loss_rate" not in self._config:
			self._config["c_term_loss_rate"] = self._defaults["c_term_loss_rate"] #rate at which an entire base equation term is replaced with 0
		if "c_term_merge_rate" not in self._config:
			self._config["c_term_merge_rate"] = self._defaults["c_term_merge_rate"] #rate at which two terms are merged with either * or / and the second term is replaced with 0
		if "c_no_mutate_rate" not in self._config:
			self._config["c_no_mutate_rate"] = self._defaults["c_no_mutate_rate"] #rate at which no mutation occures
			
		if "c_message_level" not in self._config:
			self._config["c_message_level"] = self._defaults["c_message_level"] #Amount of information to output
		
		if "c_max_solvers" not in self._config:
			self._config["c_max_solvers"] = self._defaults["c_max_solvers"] #Maximum amount of solvers remaining at the end of each day
		
		if "c_avg_terms" not in self._config:
			self._config["c_avg_terms"] = self._defaults["c_avg_terms"] #Average number of terms per solver
		if "c_stdev_terms" not in self._config:
			self._config["c_stdev_terms"] = self._defaults["c_stdev_terms"] #St. Dev of number of terms per solver
		if "c_max_terms" not in self._config:
			self._config["c_max_terms"] = self._defaults["c_max_terms"] #Hard maximum number of terms per solver
