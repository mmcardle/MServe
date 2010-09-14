from django.db import models
import random, string
import uuid

ID_FIELD_LENGTH = 200

def random_id():
    return str(uuid.uuid4())

class Base(models.Model):
    name = models.CharField(max_length=200)
    id = models.CharField(primary_key=True, max_length=ID_FIELD_LENGTH)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name;

class HostingContainer(Base):
    status = models.CharField(max_length=200)
    def save(self):
        if not self.id:
            self.id = random_id()
        super(HostingContainer, self).save()

class DataService(Base):
    container = models.ForeignKey(HostingContainer)
    status = models.CharField(max_length=200)
    def save(self):
        if not self.id:
            self.id = random_id()
        super(DataService, self).save()

class DataStager(Base):
    service = models.ForeignKey(DataService)
    file = models.FileField(upload_to="stagers/%Y/%m/%d")
    def save(self):
        if not self.id:
            self.id = random_id()
        super(DataStager, self).save()

class Auth(Base):
    #parent = models.ForeignKey(Base)
    authname = models.CharField(max_length=50)
    roles_encoded = models.TextField()

    def roles(self):
        return pickle.loads(base64.b64decode(self.roles_encoded))
