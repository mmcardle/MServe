from django.db import models
import uuid
import pickle
import base64

ID_FIELD_LENGTH = 200

def random_id():
    return str(uuid.uuid4())

class Base(models.Model):
    id = models.CharField(primary_key=True, max_length=ID_FIELD_LENGTH)

    class Meta:
        abstract = True

class NamedBase(Base):
    name = models.CharField(max_length=200)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name;

class HostingContainer(NamedBase):
    status = models.CharField(max_length=200)
    def save(self):
        if not self.id:
            self.id = random_id()
        super(HostingContainer, self).save()

class ManagementProperty(models.Model):
    container = models.ForeignKey(HostingContainer)
    property   = models.CharField(primary_key=True, max_length=200)
    value = models.CharField(max_length=200)

class DataService(NamedBase):
    container = models.ForeignKey(HostingContainer)
    status = models.CharField(max_length=200)
    def save(self):
        if not self.id:
            self.id = random_id()
        super(DataService, self).save()

class DataStager(NamedBase):
    service = models.ForeignKey(DataService)
    file = models.FileField(upload_to="%Y/%m/%d")
    def save(self):
        if not self.id:
            self.id = random_id()
        super(DataStager, self).save()

class Auth(Base):
    authname = models.CharField(max_length=50)
    description= models.CharField(max_length=200)
    methods_encoded = models.TextField()

    def methods(self):
        return pickle.loads(base64.b64decode(self.methods_encoded))

    def setmethods(self,methods):
        self.methods_encoded = base64.b64encode(pickle.dumps(methods))

    def __unicode__(self):
        return self.authname + " -> " + str(self.methods())

    class Meta:
        abstract = True

class SubAuth(Auth):
    def save(self):
        if not self.id:
            self.id = random_id()
        super(SubAuth, self).save()

class JoinAuth(models.Model):
    parent = models.CharField(max_length=50)
    child  = models.CharField(max_length=50)

    def __unicode__(self):
        return str(self.parent) + " - " + str(self.child)

class DataStagerAuth(Auth):
    stager = models.ForeignKey(DataStager)
    def save(self):
        if not self.id:
            self.id = random_id()
        super(DataStagerAuth, self).save()

class DataServiceAuth(Auth):
    dataservice = models.ForeignKey(DataService)
    def save(self):
        if not self.id:
            self.id = random_id()
        super(DataServiceAuth, self).save()

class HostingContainerAuth(Auth):
    hostingcontainer = models.ForeignKey(HostingContainer)

    def save(self):
        if not self.id:
            self.id = random_id()
        super(HostingContainerAuth, self).save()
