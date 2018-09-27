#!/usr/bin/env python
# _#_ coding:utf-8 _*_
from rest_framework import serializers

class VirtualMachineSerializer(serializers.ModelSerializer):
    class Meta:
        # model = VirtualMachine
        fields = ('ip','status','cpu','ram','hostname','host','user','os')