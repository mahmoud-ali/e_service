from django.db import models

class TcActions(models.Model):
    actiontime = models.DateTimeField()
    address = models.CharField(max_length=48, blank=True, null=True)
    userid = models.IntegerField(blank=True, null=True)
    actiontype = models.CharField(max_length=32)
    objecttype = models.CharField(max_length=32, blank=True, null=True)
    objectid = models.IntegerField(blank=True, null=True)
    attributes = models.CharField(max_length=4000)

    class Meta:
        managed = False
        db_table = 'tc_actions'


class TcAttributes(models.Model):
    description = models.CharField(max_length=4000)
    type = models.CharField(max_length=128)
    attribute = models.CharField(max_length=128)
    expression = models.CharField(max_length=4000)
    priority = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tc_attributes'


class TcCalendars(models.Model):
    name = models.CharField(max_length=128)
    data = models.BinaryField()
    attributes = models.CharField(max_length=4000)

    class Meta:
        managed = False
        db_table = 'tc_calendars'


class TcCommands(models.Model):
    description = models.CharField(max_length=4000)
    type = models.CharField(max_length=128)
    textchannel = models.BooleanField()
    attributes = models.CharField(max_length=4000)

    class Meta:
        managed = False
        db_table = 'tc_commands'


class TcCommandsQueue(models.Model):
    deviceid = models.ForeignKey('TcDevices', models.DO_NOTHING, db_column='deviceid')
    type = models.CharField(max_length=128)
    textchannel = models.BooleanField()
    attributes = models.CharField(max_length=4000)

    class Meta:
        managed = False
        db_table = 'tc_commands_queue'


class TcDeviceAttribute(models.Model):
    deviceid = models.ForeignKey('TcDevices', models.DO_NOTHING, db_column='deviceid')
    attributeid = models.ForeignKey(TcAttributes, models.DO_NOTHING, db_column='attributeid')

    class Meta:
        managed = False
        db_table = 'tc_device_attribute'


class TcDeviceCommand(models.Model):
    deviceid = models.ForeignKey('TcDevices', models.DO_NOTHING, db_column='deviceid')
    commandid = models.ForeignKey(TcCommands, models.DO_NOTHING, db_column='commandid')

    class Meta:
        managed = False
        db_table = 'tc_device_command'


class TcDeviceDriver(models.Model):
    deviceid = models.ForeignKey('TcDevices', models.DO_NOTHING, db_column='deviceid')
    driverid = models.ForeignKey('TcDrivers', models.DO_NOTHING, db_column='driverid')

    class Meta:
        managed = False
        db_table = 'tc_device_driver'


class TcDeviceGeofence(models.Model):
    deviceid = models.ForeignKey('TcDevices', models.DO_NOTHING, db_column='deviceid')
    geofenceid = models.ForeignKey('TcGeofences', models.DO_NOTHING, db_column='geofenceid')

    class Meta:
        managed = False
        db_table = 'tc_device_geofence'


class TcDeviceMaintenance(models.Model):
    deviceid = models.ForeignKey('TcDevices', models.DO_NOTHING, db_column='deviceid')
    maintenanceid = models.ForeignKey('TcMaintenances', models.DO_NOTHING, db_column='maintenanceid')

    class Meta:
        managed = False
        db_table = 'tc_device_maintenance'


class TcDeviceNotification(models.Model):
    deviceid = models.ForeignKey('TcDevices', models.DO_NOTHING, db_column='deviceid')
    notificationid = models.ForeignKey('TcNotifications', models.DO_NOTHING, db_column='notificationid')

    class Meta:
        managed = False
        db_table = 'tc_device_notification'


class TcDeviceOrder(models.Model):
    deviceid = models.ForeignKey('TcDevices', models.DO_NOTHING, db_column='deviceid')
    orderid = models.ForeignKey('TcOrders', models.DO_NOTHING, db_column='orderid')

    class Meta:
        managed = False
        db_table = 'tc_device_order'


class TcDeviceReport(models.Model):
    deviceid = models.ForeignKey('TcDevices', models.DO_NOTHING, db_column='deviceid')
    reportid = models.ForeignKey('TcReports', models.DO_NOTHING, db_column='reportid')

    class Meta:
        managed = False
        db_table = 'tc_device_report'


class TcDevices(models.Model):
    name = models.CharField("الاسم",max_length=128)
    uniqueid = models.CharField("الرقم التعريفي",unique=True, max_length=128)
    lastupdate = models.DateTimeField(blank=True, null=True)
    positionid = models.IntegerField(blank=True, null=True)
    groupid = models.ForeignKey('TcGroups', models.DO_NOTHING, db_column='groupid', blank=True, null=True)
    attributes = models.CharField(max_length=4000, blank=True, null=True)
    phone = models.CharField(max_length=128, blank=True, null=True)
    model = models.CharField(max_length=128, blank=True, null=True)
    contact = models.CharField(max_length=512, blank=True, null=True)
    category = models.CharField(max_length=128, blank=True, null=True)
    disabled = models.BooleanField(blank=True, null=True)
    status = models.CharField(max_length=8, blank=True, null=True)
    expirationtime = models.DateTimeField(blank=True, null=True)
    motionstate = models.BooleanField(blank=True, null=True)
    motiontime = models.DateTimeField(blank=True, null=True)
    motiondistance = models.FloatField(blank=True, null=True)
    overspeedstate = models.BooleanField(blank=True, null=True)
    overspeedtime = models.DateTimeField(blank=True, null=True)
    overspeedgeofenceid = models.IntegerField(blank=True, null=True)
    motionstreak = models.BooleanField(blank=True, null=True)
    calendarid = models.ForeignKey(TcCalendars, models.DO_NOTHING, db_column='calendarid', blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.name}({self.uniqueid})'

    class Meta:
        managed = False
        db_table = 'tc_devices'
        verbose_name = "جهاز تتبع"
        verbose_name_plural = "قائمة اجهزة التتبع"

class TcDrivers(models.Model):
    name = models.CharField(max_length=128)
    uniqueid = models.CharField(unique=True, max_length=128)
    attributes = models.CharField(max_length=4000)

    class Meta:
        managed = False
        db_table = 'tc_drivers'


class TcEvents(models.Model):
    type = models.CharField(max_length=128)
    eventtime = models.DateTimeField()
    deviceid = models.IntegerField(blank=True, null=True)
    positionid = models.IntegerField(blank=True, null=True)
    geofenceid = models.IntegerField(blank=True, null=True)
    attributes = models.CharField(max_length=4000, blank=True, null=True)
    maintenanceid = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tc_events'


class TcGeofences(models.Model):
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=128, blank=True, null=True)
    area = models.CharField(max_length=4096)
    attributes = models.CharField(max_length=4000, blank=True, null=True)
    calendarid = models.ForeignKey(TcCalendars, models.DO_NOTHING, db_column='calendarid', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tc_geofences'


class TcGroupAttribute(models.Model):
    groupid = models.ForeignKey('TcGroups', models.DO_NOTHING, db_column='groupid')
    attributeid = models.ForeignKey(TcAttributes, models.DO_NOTHING, db_column='attributeid')

    class Meta:
        managed = False
        db_table = 'tc_group_attribute'


class TcGroupCommand(models.Model):
    groupid = models.ForeignKey('TcGroups', models.DO_NOTHING, db_column='groupid')
    commandid = models.ForeignKey(TcCommands, models.DO_NOTHING, db_column='commandid')

    class Meta:
        managed = False
        db_table = 'tc_group_command'


class TcGroupDriver(models.Model):
    groupid = models.ForeignKey('TcGroups', models.DO_NOTHING, db_column='groupid')
    driverid = models.ForeignKey(TcDrivers, models.DO_NOTHING, db_column='driverid')

    class Meta:
        managed = False
        db_table = 'tc_group_driver'


class TcGroupGeofence(models.Model):
    groupid = models.ForeignKey('TcGroups', models.DO_NOTHING, db_column='groupid')
    geofenceid = models.ForeignKey(TcGeofences, models.DO_NOTHING, db_column='geofenceid')

    class Meta:
        managed = False
        db_table = 'tc_group_geofence'


class TcGroupMaintenance(models.Model):
    groupid = models.ForeignKey('TcGroups', models.DO_NOTHING, db_column='groupid')
    maintenanceid = models.ForeignKey('TcMaintenances', models.DO_NOTHING, db_column='maintenanceid')

    class Meta:
        managed = False
        db_table = 'tc_group_maintenance'


class TcGroupNotification(models.Model):
    groupid = models.ForeignKey('TcGroups', models.DO_NOTHING, db_column='groupid')
    notificationid = models.ForeignKey('TcNotifications', models.DO_NOTHING, db_column='notificationid')

    class Meta:
        managed = False
        db_table = 'tc_group_notification'


class TcGroupOrder(models.Model):
    groupid = models.ForeignKey('TcGroups', models.DO_NOTHING, db_column='groupid')
    orderid = models.ForeignKey('TcOrders', models.DO_NOTHING, db_column='orderid')

    class Meta:
        managed = False
        db_table = 'tc_group_order'


class TcGroupReport(models.Model):
    groupid = models.ForeignKey('TcGroups', models.DO_NOTHING, db_column='groupid')
    reportid = models.ForeignKey('TcReports', models.DO_NOTHING, db_column='reportid')

    class Meta:
        managed = False
        db_table = 'tc_group_report'


class TcGroups(models.Model):
    name = models.CharField(max_length=128)
    groupid = models.ForeignKey('self', models.DO_NOTHING, db_column='groupid', blank=True, null=True)
    attributes = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tc_groups'


class TcKeystore(models.Model):
    publickey = models.BinaryField()
    privatekey = models.BinaryField()

    class Meta:
        managed = False
        db_table = 'tc_keystore'


class TcMaintenances(models.Model):
    name = models.CharField(max_length=4000)
    type = models.CharField(max_length=128)
    start = models.FloatField()
    period = models.FloatField()
    attributes = models.CharField(max_length=4000)

    class Meta:
        managed = False
        db_table = 'tc_maintenances'


class TcNotifications(models.Model):
    type = models.CharField(max_length=128)
    attributes = models.CharField(max_length=4000, blank=True, null=True)
    always = models.BooleanField()
    calendarid = models.ForeignKey(TcCalendars, models.DO_NOTHING, db_column='calendarid', blank=True, null=True)
    notificators = models.CharField(max_length=128, blank=True, null=True)
    commandid = models.ForeignKey(TcCommands, models.DO_NOTHING, db_column='commandid', blank=True, null=True)
    description = models.CharField(max_length=4000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tc_notifications'


class TcOrders(models.Model):
    uniqueid = models.CharField(max_length=128)
    description = models.CharField(max_length=512, blank=True, null=True)
    fromaddress = models.CharField(max_length=512, blank=True, null=True)
    toaddress = models.CharField(max_length=512, blank=True, null=True)
    attributes = models.CharField(max_length=4000)

    class Meta:
        managed = False
        db_table = 'tc_orders'


class TcPositions(models.Model):
    protocol = models.CharField(max_length=128, blank=True, null=True)
    deviceid = models.ForeignKey('TcDevices', models.DO_NOTHING, db_column='deviceid')
    servertime = models.DateTimeField()
    devicetime = models.DateTimeField()
    fixtime = models.DateTimeField()
    valid = models.BooleanField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    altitude = models.FloatField()
    speed = models.FloatField()
    course = models.FloatField()
    address = models.CharField(max_length=512, blank=True, null=True)
    attributes = models.CharField(max_length=4000, blank=True, null=True)
    accuracy = models.FloatField()
    network = models.CharField(max_length=4000, blank=True, null=True)
    geofenceids = models.CharField(max_length=128, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tc_positions'


class TcReports(models.Model):
    type = models.CharField(max_length=32)
    description = models.CharField(max_length=128)
    calendarid = models.ForeignKey(TcCalendars, models.DO_NOTHING, db_column='calendarid')
    attributes = models.CharField(max_length=4000)

    class Meta:
        managed = False
        db_table = 'tc_reports'


class TcServers(models.Model):
    registration = models.BooleanField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    zoom = models.IntegerField()
    map = models.CharField(max_length=128, blank=True, null=True)
    bingkey = models.CharField(max_length=128, blank=True, null=True)
    mapurl = models.CharField(max_length=512, blank=True, null=True)
    readonly = models.BooleanField()
    attributes = models.CharField(max_length=4000, blank=True, null=True)
    forcesettings = models.BooleanField()
    coordinateformat = models.CharField(max_length=128, blank=True, null=True)
    devicereadonly = models.BooleanField(blank=True, null=True)
    limitcommands = models.BooleanField(blank=True, null=True)
    poilayer = models.CharField(max_length=512, blank=True, null=True)
    announcement = models.CharField(max_length=4000, blank=True, null=True)
    disablereports = models.BooleanField(blank=True, null=True)
    overlayurl = models.CharField(max_length=512, blank=True, null=True)
    fixedemail = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tc_servers'


class TcStatistics(models.Model):
    capturetime = models.DateTimeField()
    activeusers = models.IntegerField()
    activedevices = models.IntegerField()
    requests = models.IntegerField()
    messagesreceived = models.IntegerField()
    messagesstored = models.IntegerField()
    attributes = models.CharField(max_length=4096)
    mailsent = models.IntegerField()
    smssent = models.IntegerField()
    geocoderrequests = models.IntegerField()
    geolocationrequests = models.IntegerField()
    protocols = models.CharField(max_length=4096, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tc_statistics'


class TcUserAttribute(models.Model):
    userid = models.ForeignKey('TcUsers', models.DO_NOTHING, db_column='userid')
    attributeid = models.ForeignKey(TcAttributes, models.DO_NOTHING, db_column='attributeid')

    class Meta:
        managed = False
        db_table = 'tc_user_attribute'


class TcUserCalendar(models.Model):
    userid = models.ForeignKey('TcUsers', models.DO_NOTHING, db_column='userid')
    calendarid = models.ForeignKey(TcCalendars, models.DO_NOTHING, db_column='calendarid')

    class Meta:
        managed = False
        db_table = 'tc_user_calendar'


class TcUserCommand(models.Model):
    userid = models.ForeignKey('TcUsers', models.DO_NOTHING, db_column='userid')
    commandid = models.ForeignKey(TcCommands, models.DO_NOTHING, db_column='commandid')

    class Meta:
        managed = False
        db_table = 'tc_user_command'


class TcUserDevice(models.Model):
    userid = models.ForeignKey('TcUsers', models.DO_NOTHING, db_column='userid')
    deviceid = models.ForeignKey(TcDevices, models.DO_NOTHING, db_column='deviceid')

    class Meta:
        managed = False
        db_table = 'tc_user_device'


class TcUserDriver(models.Model):
    userid = models.ForeignKey('TcUsers', models.DO_NOTHING, db_column='userid')
    driverid = models.ForeignKey(TcDrivers, models.DO_NOTHING, db_column='driverid')

    class Meta:
        managed = False
        db_table = 'tc_user_driver'


class TcUserGeofence(models.Model):
    userid = models.ForeignKey('TcUsers', models.DO_NOTHING, db_column='userid')
    geofenceid = models.ForeignKey(TcGeofences, models.DO_NOTHING, db_column='geofenceid')

    class Meta:
        managed = False
        db_table = 'tc_user_geofence'


class TcUserGroup(models.Model):
    userid = models.ForeignKey('TcUsers', models.DO_NOTHING, db_column='userid')
    groupid = models.ForeignKey(TcGroups, models.DO_NOTHING, db_column='groupid')

    class Meta:
        managed = False
        db_table = 'tc_user_group'


class TcUserMaintenance(models.Model):
    userid = models.ForeignKey('TcUsers', models.DO_NOTHING, db_column='userid')
    maintenanceid = models.ForeignKey(TcMaintenances, models.DO_NOTHING, db_column='maintenanceid')

    class Meta:
        managed = False
        db_table = 'tc_user_maintenance'


class TcUserNotification(models.Model):
    userid = models.ForeignKey('TcUsers', models.DO_NOTHING, db_column='userid')
    notificationid = models.ForeignKey(TcNotifications, models.DO_NOTHING, db_column='notificationid')

    class Meta:
        managed = False
        db_table = 'tc_user_notification'


class TcUserOrder(models.Model):
    userid = models.ForeignKey('TcUsers', models.DO_NOTHING, db_column='userid')
    orderid = models.ForeignKey(TcOrders, models.DO_NOTHING, db_column='orderid')

    class Meta:
        managed = False
        db_table = 'tc_user_order'


class TcUserReport(models.Model):
    userid = models.ForeignKey('TcUsers', models.DO_NOTHING, db_column='userid')
    reportid = models.ForeignKey(TcReports, models.DO_NOTHING, db_column='reportid')

    class Meta:
        managed = False
        db_table = 'tc_user_report'


class TcUserUser(models.Model):
    userid = models.ForeignKey('TcUsers', models.DO_NOTHING, db_column='userid')
    manageduserid = models.ForeignKey('TcUsers', models.DO_NOTHING, db_column='manageduserid', related_name='tcuseruser_manageduserid_set')

    class Meta:
        managed = False
        db_table = 'tc_user_user'


class TcUsers(models.Model):
    name = models.CharField(max_length=128)
    email = models.CharField(unique=True, max_length=128)
    hashedpassword = models.CharField(max_length=128, blank=True, null=True)
    salt = models.CharField(max_length=128, blank=True, null=True)
    readonly = models.BooleanField()
    administrator = models.BooleanField(blank=True, null=True)
    map = models.CharField(max_length=128, blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    zoom = models.IntegerField()
    attributes = models.CharField(max_length=4000, blank=True, null=True)
    coordinateformat = models.CharField(max_length=128, blank=True, null=True)
    disabled = models.BooleanField(blank=True, null=True)
    expirationtime = models.DateTimeField(blank=True, null=True)
    devicelimit = models.IntegerField(blank=True, null=True)
    userlimit = models.IntegerField(blank=True, null=True)
    devicereadonly = models.BooleanField(blank=True, null=True)
    phone = models.CharField(max_length=128, blank=True, null=True)
    limitcommands = models.BooleanField(blank=True, null=True)
    login = models.CharField(max_length=128, blank=True, null=True)
    poilayer = models.CharField(max_length=512, blank=True, null=True)
    disablereports = models.BooleanField(blank=True, null=True)
    fixedemail = models.BooleanField(blank=True, null=True)
    totpkey = models.CharField(max_length=64, blank=True, null=True)
    temporary = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tc_users'
