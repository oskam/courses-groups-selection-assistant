#!/bin/bash

python manage.py dumpdata -e contenttypes -e auth -e admin.logentry -e sessions -e students -e schedules.timetable --indent 2 > db.json