import datetime

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms

class ReportHandler(db.Model):
    '''configures the datastore to be used to store form variables.
    Properties:
    category-category of the report
    location-where the report took place
    source-source of the report
    description-report description
    audiofile-an audio file to be uploaded'''
    category=db.CategoryProperty()
    date=db.IntegerProperty(default=0)
    create=db.DateProperty(default=datetime.date(2011,4,1))
    location=db.StringProperty(multiline=True)
    source=db.StringProperty(multiline=True)
    inciter=db.StringProperty(multiline=True)
    description=db.StringProperty(multiline=True)
    audiofile=db.BlobProperty()
    audiofileBool=db.BooleanProperty(default=False)
    verified=db.BooleanProperty(default=False)
class TagHandler(db.Model):
    '''datastore for tags
    Properties:
    tag-name of the tag
    date-datestamp'''
    tag=db.CategoryProperty();
    date=db.DateTimeProperty(auto_now_add=True)
    
class UserReportsNo(db.Model):
    '''Stores the number of user reports sent in by the user
    Properties:
    author-userID
    count-number of reports sent In
    '''
    author=db.UserProperty()
    count=db.IntegerProperty(default=0)
    
class ItemForm(djangoforms.ModelForm):
    class Meta:
        model = ReportHandler
        exclude = ['date','create','audiofile','audiofileBool','verified']
    
def get_user_report_no(cur_user):
    '''Retrieves number of reports a user has submitted'''
    if(cur_user==users.get_current_user()):
        return UserReportsNo.count

def set_user_report_no(cur_user):
    '''Increments number of reports a user has submitted'''
    user=users.get_current_user()
    count=0
    ReportNo=UserReportsNo()
    if(user):
        UserReportsNo().count+=1
        count+=1
    else:
        UserReportsNo().count+=0    
    return ReportNo.put()
def get_tags_no(tag):
    '''retrieves the number of tags according to a specific search term'''
    tags=TagHandler.get_by_key_name(tag)
    for count in tags:
        count+=1
    return count

def get_reports_newest(self):
    '''retrieves the submitted reports by all users for a current day'''
    reports=db.GqlQuery("SELECT * FROM ReportHandler WHERE verified=True ORDER BY date DESC")
    for report in reports:
        self.response.out.write('%s,%s,%s,%s,%s,%s\n' % (report.description ,report.location ,report.source ,report.inciter ,report.category ,report.create))

def get_reports_by_location(self):
    '''retrieves reports submitted in order of location'''
    reports=db.GqlQuery("SELECT * FROM ReportHandler WHERE verified=True ORDER BY location DESC")
    for report in reports:
        self.response.out.write('%s,%s,%s,%s,%s,%s\n' % (report.description ,report.location ,report.source ,report.inciter ,report.category ,report.create))
def get_reports_by_category(self):
    '''retrieves reports submitted in order of category'''
    reports=db.GqlQuery("SELECT * FROM ReportHandler WHERE verified=True ORDER BY category DESC")
    for report in reports:
        self.response.out.write('%s,%s,%s,%s,%s,%s\n' % (report.description ,report.location ,report.source ,report.inciter ,report.category ,report.create))
def get_reports_by_source(self):
    '''retrieves reports submitted in order of source'''
    reports=db.GqlQuery("SELECT * FROM ReportHandler WHERE verified=True ORDER BY source DESC")
    for report in reports:
        self.response.out.write('%s,%s,%s,%s,%s,%s\n' % (report.description ,report.location ,report.source ,report.inciter ,report.category ,report.create))
def get_reports_by_inciter(self):
    '''retrieves reports submitted in order of source'''
    reports=db.GqlQuery("SELECT * FROM ReportHandler WHERE verified=True ORDER BY inciter DESC")
    for report in reports:
        self.response.out.write('%s,%s,%s,%s,%s,%s\n' % (report.description ,report.location ,report.source ,report.inciter ,report.category ,report.create))
def get_advanced_report(self,category,location,source,inciter,date1,date2):
    '''retrieves reports based on multiple search parameters'''
    if category is None:
        startdate=datetime.datetime.strptime(date1,'%Y,%m,%d')
        endate=datetime.datetime.strptime(date2,'%Y,%m,%d')
        reports=ReportHandler.gql("WHERE location =:1 AND source =:2 AND inciter =:3 AND create >=:4 AND create <=:5",location,source,inciter,startdate,endate)
    elif location is None:
        startdate=datetime.datetime.strptime(date1,'%Y,%m,%d')
        endate=datetime.datetime.strptime(date2,'%Y,%m,%d')
        reports=ReportHandler.gql("WHERE category =:1 AND source =:2 AND inciter =:3 AND create >=:4 AND create <=:5",category,source,inciter,startdate,endate)
    elif source is None:
        startdate=datetime.datetime.strptime(date1,'%Y,%m,%d')
        endate=datetime.datetime.strptime(date2,'%Y,%m,%d')
        reports=ReportHandler.gql("WHERE category =:1 AND location =:2 AND inciter =:3 AND create >=:4 AND create <=:5",category,location,inciter,startdate,endate)
    elif inciter is None:
        startdate=datetime.datetime.strptime(date1,'%Y,%m,%d')
        endate=datetime.datetime.strptime(date2,'%Y,%m,%d')
        reports=ReportHandler.gql("WHERE category =:1 AND location =:2 AND source =:3 AND create >=:4 AND create <=:5",category,location,source,startdate,endate)
    elif date1 is None or date2 is None:
        reports=ReportHandler.all().filter('category =',category).filter('location =', location).filter('source =',source).filter('inciter =',inciter).filter('create >=',startdate).filter('create <=',endate).fetch(10)
        #reports=ReportHandler.gql("WHERE category =:1 AND location =:2 AND source =:3 AND inciter =:4",category,location,source,inciter)
    elif date2 is None:
        reports=ReportHandler.gql("WHERE category =:1 AND location =:2 AND source =:3 AND inciter =:4",category,location,source,inciter)
    else:
        startdate=datetime.datetime.strptime(date1,'%Y,%m,%d')
        endate=datetime.datetime.strptime(date2,'%Y,%m,%d')
        reports=ReportHandler.all().filter('category =',category).filter('location =', location).filter('source =',source).filter('inciter =',inciter).filter('create >=',startdate).filter('create <=',endate).fetch(10)
        #reports=ReportHandler.gql("WHERE category =:1 AND location =:2 AND source =:3 AND inciter =:4 AND create >=:5 AND create <=:6",category,location,source,inciter,startdate,endate)
    if reports:
        for report in reports:
            self.response.out.write('%s,%s,%s,%s,%s,%s\n' % (report.description ,report.location ,report.source ,report.inciter ,report.category ,report.create))
    else:
        self.response.out.write('No Results')
def get_tags_by_id(name):
    '''retrieves reports according to tags'''
    tags=db.GqlQuery("SELECT * FROM Tag Handler WHERE tag=:1 DESC",name)
    for tag in tags:
        number=get_tags_no(name)
        return tag, number
def post_form_variables(cat,loc,tsource,inciter,desc):
    try:
        now = datetime.date.today()
        report=ReportHandler()
        report.category=cat
        report.create=now
        report.location=loc
        report.source=tsource
        report.inciter=inciter
        report.description=desc
        
        if (report.put()):
            message='success'
        else:
            message='error'
        return message
    except db.Error:
            return None 
def post_tag_variables(cat,loc,tsource,inciter):
    now = datetime.datetime.now()
    tag=TagHandler()
    try:
        if cat is not None:
            tag.tag=cat
            tag.date=now
            tag.put()
#t=TagHandler(
#tag=cat,
#date=now.isoformat()[:19]
#)
        if loc is not None:
            tag.tag=loc
            tag.date=now.isoformat()
            tag.put()
        if tsource is not None:
            tag.tag=tsource
            tag.date=now.isoformat()
            tag.put()
        if inciter is not None:
            tag.tag=inciter
            tag.date=now.isoformat()
            tag.put()
    except db.Error:
        return None 