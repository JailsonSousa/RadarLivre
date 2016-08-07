# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from curses.ascii import NL
import datetime
import logging

from django.contrib.auth.models import User
from django.db import models
from django.db.models.fields import CharField, DecimalField, IntegerField, BigIntegerField, \
    BooleanField, TextField, DateTimeField, DateField, URLField, EmailField
from django.db.models.fields.files import ImageField, FileField
from django.db.models.fields.related import ForeignKey, \
    OneToOneField
from imagekit.models.fields import ImageSpecField
from pilkit.processors.resize import ResizeToFill

import uuid


logger = logging.getLogger("radarlivre.log")

class Collector(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="collectors", null=True)
    
    latitude  = DecimalField(max_digits=40, decimal_places=20, default=0.0)
    longitude = DecimalField(max_digits=40, decimal_places=20, default=0.0)
    timestamp = BigIntegerField(default=0)
    timestampData = BigIntegerField(default=0)
    
    def getDate(self):
        return datetime.datetime.fromtimestamp(
            int(self.timestamp/1000)
        ).strftime('%d/%m/%Y %H:%M:%S')
    
    def __unicode__(self):
        return "Active collector from " + self.user.username
    
class Airplane(models.Model):
    
    icao = CharField(max_length=16, primary_key=True)
    
    
class AirplaneInfo(models.Model):
    
    airplane = OneToOneField(Airplane, on_delete=models.CASCADE)
    flight = CharField(max_length=100, blank=True, default="")
    airline = CharField(max_length=100, blank=True, default="")
    airlineCountry = CharField(max_length=100, blank=True, default="")
    
    # Airplane position
    latitude = DecimalField(max_digits=40, decimal_places=20, default=0.0)
    longitude = DecimalField(max_digits=40, decimal_places=20, default=0.0)
    altitude = DecimalField(max_digits=40, decimal_places=20, default=0.0)
    
    # Airplane velocity
    verticalVelocity = DecimalField(max_digits=40, decimal_places=20, default=0.0)
    horizontalVelocity = DecimalField(max_digits=40, decimal_places=20, default=0.0)
    
    #Airplane angle
    groundTrackHeading = DecimalField(max_digits=40, decimal_places=20, default=0.0)
    
    #Last observation date time generated by server
    timestamp = BigIntegerField(default=0)
    
    def __unicode__(self):
        return "Airplane info:" + str(self.airplane) + " " + str( datetime.datetime.fromtimestamp( int((self.timestamp)/1000) ).strftime('%d-%m-%Y %H:%M:%S') )
    
    
class Airport(models.Model):
    
    # Airport identification
    prefix    = CharField(max_length=100, primary_key=True)
    name      = CharField(max_length=100, blank=True, default='', null=True)
    
    # Airport location
    country   = CharField(max_length=100, blank=True, default='', null=True)
    state     = CharField(max_length=100, blank=True, default='', null=True)
    city      = CharField(max_length=100, blank=True, default='', null=True)
    latitude  = DecimalField(max_digits=40, decimal_places=20, default=0.0)
    longitude = DecimalField(max_digits=40, decimal_places=20, default=0.0)

    type = CharField(max_length=100, blank=True, default='', null=True)
    
    def __unicode__(self):
        return "Airport " + self.prefix + " - " + self.name
        
        
class Flight(models.Model):

    # Flight identification
    callsign = CharField(max_length=100, primary_key=True)
    
    # For each route, can exists many airplanes
    airplane = OneToOneField(Airplane, blank=True, default=None, null=True, related_name='flight', on_delete=models.CASCADE)
    airline = CharField(max_length=100, blank=True, default="", null=True)
    airlineCountry = CharField(max_length=100, blank=True, default="", null=True)
    
    # Route origin and destine
    origin  = ForeignKey(Airport, blank=True, default=None, null=True, related_name='flights_leaving')
    destine = ForeignKey(Airport, blank=True, default=None, null=True, related_name='flights_coming')
    
    def __unicode__(self):
        return "Flight from " + str(self.origin) + " to " + str(self.destine)
    
class Observation(models.Model):
    
    # User collector that sent the observation
    collector = ForeignKey(Collector, related_name="observations", default=None, null=True)
    
    # Airplane observed
    airplane = ForeignKey(Airplane, null=True, blank=True, default=None, related_name='observations')
    flight = ForeignKey(Flight, null=True, blank=True, default=None, related_name='observations')
     
    # Airplane position
    latitude  = DecimalField(max_digits=40, decimal_places=20, default=0.0)
    longitude = DecimalField(max_digits=40, decimal_places=20, default=0.0)
    altitude  = DecimalField(max_digits=40, decimal_places=20, default=0.0)
    
    # Airplane velocity
    verticalVelocity = DecimalField(max_digits=40, decimal_places=20, default=0.0)
    horizontalVelocity = DecimalField(max_digits=40, decimal_places=20, default=0.0)
     
    #Airplane angle
    groundTrackHeading  = DecimalField(max_digits=40, decimal_places=20, default=0.0)
    
    # Observation date time generated by server
    timestamp      = BigIntegerField(default=0)
    timestampSent  = BigIntegerField(default=0)
    
    # Originals ADS-B messages
    messageDataId           = CharField(max_length=100, blank=True, default='')
    messageDataPositionEven = CharField(max_length=100, blank=True, default='')
    messageDataPositionOdd  = CharField(max_length=100, blank=True, default='')
    messageDataVelocity     = CharField(max_length=100, blank=True, default='')
    
    def __unicode__(self):
        return "Observation of airplane " + str(self.airplane)

    def generateAirplaneInfo(self):
        airplaneInfo = AirplaneInfo()
        try:
            airplaneInfo = AirplaneInfo.objects.get(airplane=self.airplane)
        except AirplaneInfo.DoesNotExist:
            pass

        airplaneInfo.airplane=self.airplane
        airplaneInfo.flight = self.flight.callsign
        airplaneInfo.airline = self.flight.airline
        airplaneInfo.airlineCountry = self.flight.airlineCountry

        # Airplane position
        airplaneInfo.latitude = self.latitude
        airplaneInfo.longitude = self.longitude
        airplaneInfo.altitude = self.altitude

        # Airplane velocity
        airplaneInfo.verticalVelocity = self.verticalVelocity
        airplaneInfo.horizontalVelocity = self.horizontalVelocity

        # Airplane angle
        airplaneInfo.groundTrackHeading = self.groundTrackHeading

        airplaneInfo.timestamp = self.timestamp

        airplaneInfo.save()
 
 
# Used to store project informations
class About(models.Model):
    
    title    = CharField(max_length=1000, blank=True, default="")
    subtitle = CharField(max_length=1000, blank=True, default="")
    info     = TextField(blank=True, default="")
    
    index = IntegerField(default=0)
    
    externURL = URLField(verbose_name="Extern link", default="", blank=True)
    
    image = ImageField(upload_to="about_images", null=True)
    
    largeImage = ImageSpecField(source="image",
                                processors=[ResizeToFill(1920, 1080)],
                                format='JPEG',
                                options={'quality': 75, 'progressive': True})
    
    mediumImage = ImageSpecField(source="image",
                                 processors=[ResizeToFill(1280, 720)],
                                 format='JPEG',
                                 options={'quality': 75, 'progressive': True})
    
    smallImage = ImageSpecField(source="image",
                                processors=[ResizeToFill(640, 360)],
                                format='JPEG',
                                options={'quality': 75, 'progressive': True})
    
    def getShortDescription(self):
        return str(self.title + " - " + self.subtitle[:50] + "...")
    
    def toHTML(self):
        return self.info.replace("<p", "<p class=\"rl-document__paragraph\"")\
            .replace("<span", "<span class=\"rl-document__title\"")
    
    def __unicode__(self):
        return self.title + " - " + self.subtitle
    
# Send notify to all app's
class Notify(models.Model):
    
    title = CharField(max_length=1000, blank=True, default="")
    subtitle = CharField(max_length=1000, blank=True, default="")
    info = TextField(blank=True, default="")
    
    showDate = DateTimeField()
    
    vibrate = BooleanField(default=True)
    song = BooleanField(default=False)
    
    def __unicode__(self):
        return self.title + " - " + self.subtitle


# Radar Livre Softwares
class Software(models.Model): 
    
    title = CharField(max_length=1000, blank=True, default="")
    
    versionName = CharField(max_length=1000, blank=True, default="")
    versionCode = IntegerField(default=0)
    
    lastUpdate = DateField(default=0)
    
    executable = FileField(
        upload_to="softwares/collector"
    )

    