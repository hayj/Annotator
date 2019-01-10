	def addValidityFunctDEPRECATED(self, label, funct):
		"""
			You can give validity functions for each labels:
			annotator.addValidityFunct("firstLabel", lambda x: None if x < 0.0 or x > 1.0 else "The value must be between 0.0 and 1.0")
			These function have to return None or an error message.
		"""
		self.validityFuncts[label] = funct
