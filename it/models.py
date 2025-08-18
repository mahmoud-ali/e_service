from django.db import models
from django.utils.translation import gettext_lazy as _

from hr.models import EmployeeBasic

class Application(models.Model):
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.name} {self.version or ''}".strip()


class ComputerTemplate(models.Model):
    OS_TYPES = [
        ("windows", "Windows"),
        ("linux", "Linux"),
        ("macos", "macOS"),
        ("other", "Other"),
    ]

    os_type = models.CharField(max_length=50, choices=OS_TYPES)
    os_version = models.CharField(max_length=50)
    applications = models.ManyToManyField(Application, related_name="templates")

    def __str__(self):
        return f"{self.get_os_type_display()} {self.os_version} Template"


class Computer(models.Model):
    COMPUTER_TYPES = [
        ("desktop", "Desktop"),
        ("laptop", "Laptop"),
    ]

    code = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=20, choices=COMPUTER_TYPES)
    template = models.ForeignKey(ComputerTemplate, on_delete=models.CASCADE, related_name="computers")

    def __str__(self):
        return f"{self.code} ({self.get_type_display()})"


class NetworkAdapter(models.Model):
    CONNECTIVITY_TYPES = [
        ("wired", "Wired"),
        ("wireless", "Wireless"),
    ]

    computer = models.ForeignKey(Computer, on_delete=models.CASCADE, related_name="network_adapters")
    model = models.CharField(max_length=100)
    connectivity_type = models.CharField(max_length=20, choices=CONNECTIVITY_TYPES)

    def __str__(self):
        return f"{self.model} ({self.get_connectivity_type_display()})"


class Peripheral(models.Model):
    PERIPHERAL_TYPES = [
        ("display", "External display"),
        ("keyboard", "Keyboard"),
        ("mouse", "Mouse"),
        ("printer", "Printer"),
        ("processor", "Processor"),
        ("memory", "Memory"),
        ("hard_drive", "Hard drive"),
        ("graphics_card", "Graphics card"),
        ("other", "Other"),
    ]

    computer = models.ForeignKey(Computer, on_delete=models.CASCADE, related_name="peripherals")
    type = models.CharField(max_length=20, choices=PERIPHERAL_TYPES)
    name = models.CharField(max_length=100, blank=True, null=True)
    connectivity_type = models.CharField(max_length=20, blank=True, null=True)
    specifications = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name or self.type} ({self.connectivity_type})"


class AccessPoint(models.Model):
    computer = models.ForeignKey(Computer, on_delete=models.CASCADE, related_name="access_points")
    name = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.model})"


class EmployeeComputer(models.Model):
    employee = models.ForeignKey(EmployeeBasic, on_delete=models.PROTECT,verbose_name=_("employee_name"))
    computer = models.ForeignKey(Computer, on_delete=models.CASCADE, related_name="employee_computers")

    def __str__(self):
        return f"{self.employee}({self.computer})"

class Conversation(models.Model):
    master = models.ForeignKey(EmployeeComputer, on_delete=models.PROTECT)
    created_at = models.DateTimeField(_("created_at"),auto_now_add=True,editable=False,)
    question = models.TextField()
    answer = models.TextField()    