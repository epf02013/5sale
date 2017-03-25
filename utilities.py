from flask import session
def calc_index(time) :
	return time.hour*2+(time.minute/30)


