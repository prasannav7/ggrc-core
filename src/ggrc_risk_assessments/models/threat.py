# Copyright (C) 2013 Google Inc., authors, and contributors <see AUTHORS file>
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
# Created By: dan@reciprocitylabs.com
# Maintained By: dan@reciprocitylabs.com


from ggrc import db
from ggrc.models.mixins import Timeboxed, BusinessObject


class Threat(Timeboxed, BusinessObject, db.Model):
  __tablename__ = 'threats'
  _title_uniqueness = False
  _slug_uniqueness = False
