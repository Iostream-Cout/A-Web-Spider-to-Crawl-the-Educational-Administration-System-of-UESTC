# A-Web-Spider-to-Crawl-the-Educational-Administration-System-of-UESTC

[Introduction]
	This package provides a web spider interface to crawl the Educational Administration System of UESTC(University of Electronic Science of China). The spider does no harm to the system if used properly and legally. 
	The basic functions of the package include logging into the system by posting your username and your password, getting your final score of a certain course and getting your GPA. 
	The interface of the package is extensible. You can develop your own interfaces according to your need.

[APIs]
	
Functions:
	
getGrade(username, password, course_name):
  Returns your final score corresponding to the course name you provide.If no course is found to match the course name, it will return None.
		
getGPA(username, password):
  Returns your GPA in float type.
	
Class:
	
Login(object):
		
Interfaces:
			
__init__(self, username, password):
  When creating a Login object you should provide your username, and your password.
			
log(self, username, username):
  This method simply does the work of logging into the system and does nothing else.
				
visit(self, url):
  This method returns a Response object after making an HTTP request to the provided URL.If the request fails to get the right response, it will call the log method again and again until the aimed page is available.
