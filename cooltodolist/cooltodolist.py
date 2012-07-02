import os
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users
from google.appengine.ext import db

class TodoList(db.Model):
	creator = db.UserProperty()
	todo = db.StringProperty()
	status = db.IntegerProperty()
	tag = db.StringProperty()

def todo_key(key_name=None):
	return db.Key.from_path('TodoList',key_name or 'default_key')

class MainPage(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			activetodo = TodoList.gql("WHERE creator=:1 AND status=1", user)
			completetodo = TodoList.gql("WHERE creator=:1 AND status=0", user)
			url = users.create_logout_url(self.request.uri)
			url_text = "Logout"
		else:
			url = users.create_login_url(self.request.uri)
			url_text = "Login"
		
		template_path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(template_path, locals()))

	def post(self):
		user = users.get_current_user()
		if user:
			todo = self.request.get('todo')
			tt = TodoList(parent=todo_key())
			tt.creator = user
			tt.todo = todo
			tt.status = 1
			tt.tag = 'default'
			tt.put()
			self.redirect("/")
		else:
			self.redirect(users.create_login_url(self.request.uri))

class Complete(webapp.RequestHandler):
	def get(self):
		id = self.request.get('id')
		todo = TodoList.get(id)
		todo.status=0
		todo.put()
		self.redirect("/")

class Incomplete(webapp.RequestHandler):
	def get(self):
		id = self.request.get('id')
		todo = TodoList.get(id)
		todo.status=1
		todo.put()
		self.redirect("/")
		
class Delete(webapp.RequestHandler):
	def get(self):
		id = self.request.get('id')
		todo = TodoList.get(id)
		todo.delete()
		

application = webapp.WSGIApplication([('/', MainPage),('/complete', Complete),('/delete', Delete),('/incomplete', Incomplete)], debug=True)
if __name__ == "__main__":
	run_wsgi_app(application)
