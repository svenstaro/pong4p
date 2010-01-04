class Config_Loader(object):
	def __init__(self,filename):
		self.filename = filename
		self.content = {}
		self.read()
		
	def read(self):
		c_file = open(self.filename, "r")
		for line in c_file:
			#line=line[0]
			line=line.strip()
			if not (line=="" or line[0]=="#"):
				try:
					auslese = line.split("=")
					auslese[1] = auslese[1].split("#")[0].strip()
					auslese[0] = auslese[0].strip()  
					self.content[auslese[0].lower()]=auslese[1]
				except:
					pass
		c_file.close()
	
	def getInteger(self,name):
		try: return int(self.content[name.lower()])
		except: return -1
		
	def getString(self,name):
		return self.content[name.lower()]
		return -1
	
	def getBoolean(self,name):
		trues = ["true","on","yes","1"]
		falses = ["false","off","no","0"]
		try: 
			if self.content[name.lower()].lower() in trues: return True
			elif self.content[name.lower()].lower() in falses: return False
			else: return -1
		except: return -1
	
	def setString(self,name,value):
		strings = []
		self.content[name]=value
		changed = False
		c_file = open(self.filename)
		for line in c_file:
			line=line.strip()
		
			auslese = line.split("=")
			auslese[0]=auslese[0].strip()  
			if auslese[0].lower()==name.lower():
				ll = name+" = "+value
				if len(auslese)>1:
					comment = auslese[1].split("#")
					auslese[0] = auslese[0].strip()
					if (len(comment)>1): 
						comment[1].strip()
						ll=ll+" # "+comment[1]
				changed = True
				strings.append(ll+"\n")
			else:
				strings.append(line+"\n")
		
		if not changed:
			strings.append(name+" = "+value)
		c_file.close()
		
		w_file = open(self.filename, "w")
		w_file.writelines(strings)
		w_file.close()


def valid_ip(ip_str):
	if len(ip_str.split()) == 1:
		ipList = ip_str.split('.')
		if len(ipList) == 4:
			for i, item in enumerate(ipList):
				try:
					ipList[i] = int(item)
				except:
					return False
				if not isinstance(ipList[i], int):
					return False
			if max(ipList) < 256:
				return True
			else:
				return False
		else:
			return False
	else:
		return False

if __name__=="__main__":
	cl=Config_Loader('.pong4p')
	cl.setString("button_border_width","2")
	cl.setString("button_border_height","2")