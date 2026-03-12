#!/bin/bash
systemctl list-unit-files | grep -q slurmctld.service
