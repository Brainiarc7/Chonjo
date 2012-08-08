from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp import template
import os
import cgi
import wsgiref.handlers
import model
import datetime
import logging

class ReportHandler(webapp.RequestHandler):
    def get(self):
 
        cat=self.request.get('category')
        loc=self.request.get('location')
        tsource=self.request.get('source')
        inciter=self.request.get('inciter')
        desc=self.request.get('description')
        
        response=model.post_form_variables(cat,loc,tsource,inciter,desc)
        model.post_tag_variables(cat,loc,tsource,inciter)
        self.response.out.write(response)
        logging.info("Response:%s" %response)
    def post(self):
        cat=self.request.get('category')
        loc=self.request.get('location')
        tsource=self.request.get('source')
        inciter=self.request.get('inciter')
        desc=self.request.get('description')
        
        response=model.post_form_variables(cat,loc,tsource,inciter,desc)
        model.post_tag_variables(cat,loc,tsource,inciter)
        logging.info("Response:%s" %response)
class MainHandler(webapp.RequestHandler):
    def get(self):
        logging.info('Sort Parameter:%s',self.request.get('sort'))
        if (self.request.get('sort')=='category'):
            (model.get_reports_by_category(self))
        if (self.request.get('sort')=='location'):
            (model.get_reports_by_location(self))
        if (self.request.get('sort')=='source'):
            (model.get_reports_by_source(self))
        if (self.request.get('sort')=='inciter'):
            (model.get_reports_by_inciter(self))
        else:
            (model.get_reports_newest(self))
class TagHandler(webapp.RequestHandler):
    def get(self):
        name=self.request.get('tag')
        logging.info('Tag Parameter:%s',name)
        tag, num=model.get_tags_by_id(name)
        self.response.out.write(tag)
        self.response.out.write(',')
        self.response.out.write(num)
        self.response.out.write('\n')
class AdvancedSearch(webapp.RequestHandler):
    def get(self):
        category=self.request.get('category')
        location=self.request.get('location')
        source=self.request.get('source')
        inciter=self.request.get('inciter')
        date1=self.request.get('date1')
        date2=self.request.get('date2')
        self.response.out.write(model.get_advanced_report(self,category, location, source, inciter, date1, date2))
        
class testHTML(webapp.RequestHandler):
    def get(self):
        
        self.response.out.write("""<html>
                               <head>
                               <link type="text/css" rel="stylesheet" href="/stylesheets/site.css" />
                               </head> <body>""")

        reports = model.ReportHandler.gql("WHERE verified=True ORDER BY date DESC LIMIT 10")


        itemform=model.ItemForm()
        template_values ={
            'reports':reports,
            'itemform':itemform
        }
        path = os.path.join(os.path.dirname(__file__), 'report.html')
        self.response.out.write(template.render(path, template_values))
    def post(self):
        data = model.ItemForm(data=self.request.POST)
        now=datetime.date.today()
        if data.is_valid():
            # Save the data, and redirect to the view page
            entity = data.save(commit=False)
            entity.create=now
            entity.put()
            self.redirect('/test')
        else:
            template_values ={
                'data':data,
            }
            path = os.path.join(os.path.dirname(__file__), 'report.html')
            self.response.out.write(template.render(path, template_values))
           # self.response.out.write('<html><body>'
           #                         '<form action="/test" method="post">'
            #                        '<table>')
            #self.response.out.write(data)
           # self.response.out.write('</table>'
            #                        '<div><input type="submit" value="Report"></div>'
            #                        '</form></body></html>')

       #report = model.ReportHandler()

        #report.category = self.request.get('category')
       # report.location= self.request.get('location')
       # report.date=
       # report.source= self.request.get('source')
        #report.description=self.request.get('description')
        #report.audiofile= self.request.get('audiofile')
        #report.put()
       # self.redirect('/test')       
class AdminPage(webapp.RequestHandler):
    def get(self):
        user=users.get_current_user()
        url = users.create_logout_url(self.request.uri)
        url_link='Logout'
        reports = db.GqlQuery("SELECT * FROM ReportHandler WHERE verified=False")
        count=0
        for item in reports:
            count+=1
        template_values ={
            'reports':reports,
            'user':user,
            'url':url,
            'url_link':url_link,
            'count':count,
        }
        path = os.path.join(os.path.dirname(__file__), 'admin.html')
        self.response.out.write(template.render(path, template_values))
        
    def post(self):
        if(self.request.get('validate')):
            description=self.request.get('desc')
            logging.info("Desc:%s" %description)
            queries=model.ReportHandler.gql("WHERE description = :1",
                                description)
            update=queries.fetch(limit=1)
            curr=update[0]
            curr.category=self.request.get('drop')
            curr.description=description
            curr.verified=True
            curr.put()
            self.redirect('/admin') 
        else:
            self.redirect('/admin')      

class Hints(webapp.RequestHandler):
    def get(self):
        if(self.request.get('hint')):
            location=self.request.get('location')
            date=self.request.get('date')
            id=int(self.request.get('id'))
            message='No matches returned'
            logging.info("Location:%s" %location)
            logging.info("Date:%s" %date)
            logging.info("ID:%s" %id)
            if location is not None and date is not None:
                query1=model.ReportHandler.gql("WHERE verified=True AND create=DATE(:1)",date)
                query2=model.ReportHandler.gql("WHERE location=:1 AND create=DATE(:2) AND verified=True",location,date)
                count2=0
                count1=0
                count3=0
                if query1 is not None:
                    for item1 in query1:
                        count1+=1
                        logging.info("Count1:%d" %count1)
                    for item2 in query2:
                        count2+=1 
                        logging.info("Count2:%d" %count2)
                    if count1!=0 or count2!=0:
                        count3=count2 * 100 / count1
                        logging.info("Count3:%d" %count3)
                    template_values ={
                    'count3':count3,
                    'count2':count2,
                    'query2':query2,
                    'id':id,
                    'message':message,
                    'date':date,
                    'location':location,
                    }
                    path = os.path.join(os.path.dirname(__file__), 'hints.html')
                    self.response.out.write(template.render(path, template_values))
                else:
                    template_values ={
                    'message':message,
                    'count3':count3,
                    'id':id,
                    }
                    path = os.path.join(os.path.dirname(__file__), 'hints.html')
                    self.response.out.write(template.render(path, template_values))
            else:
                self.redirect('/test')
        
    def post(self):
        if(self.request.get('back')):
            self.redirect('/admin')
class Generate(webapp.RequestHandler):
    def post(self):
        if self.request.get('generate'):
            param=self.request.get('param')
            day=int(self.request.get('days'))
            gap=datetime.date.today() - datetime.timedelta(days=day)
            logging.info("param:%s" %param)
            logging.info("day:%s" %day)
            logging.info("gap:%s" %gap)
            count=0
            if param=='Category':
                queries=model.ReportHandler.gql("WHERE  create>=:1 ORDER BY create,category",gap)
            elif param=='Location':
                queries=model.ReportHandler.gql("WHERE  create>=:1 ORDER BY create,location",gap)
            elif param=='Source':
                queries=model.ReportHandler.gql("WHERE  create>=:1 ORDER BY create,source",gap)
            elif param=='Inciter':
                queries=model.ReportHandler.gql("WHERE  create>=:1 ORDER BY create,inciter",gap)
            for item in queries:
                count+=1
        template_values ={
            'queries':queries,
            'count':count,
            'param':param,
            'day':day
        }
        path = os.path.join(os.path.dirname(__file__), 'generate.html')
        self.response.out.write(template.render(path, template_values))
    def get(self):
        template_values ={
        }
        path = os.path.join(os.path.dirname(__file__), 'generate.html')
        self.response.out.write(template.render(path, template_values))
    
        
application = webapp.WSGIApplication(
    [
        ('/', MainHandler),
        ('/tags',TagHandler),
        ('/report',ReportHandler),
        ('/test',testHTML),
        ('/admin',AdminPage),
        ('/advanced',AdvancedSearch),
        ('/hint',Hints),
        ('/generate',Generate)
    ], debug=True)

def main():
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()
