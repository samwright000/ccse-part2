"""
This file is used for validation
Here we have a function which checks to make sure the data entered doesn't contain bad charatercs. 
it checks for ;, ', ", select, drop, insert. 
"""

def checkforsqlinjection(text):
    if ";" in text or "'" in text or '"' in text or "select" in text.lower() or "drop" in text.lower() or "insert" in text.lower():
            return 1
    
    else:
          return 2
