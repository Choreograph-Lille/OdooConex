# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2018 ArkeUp (<http://www.arkeup.fr>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
import datetime
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)


def last_date_of_month(today=False):
    """
    :param today:
    :return: last date of month
    """
    if not today:
        return False
    try:
        return datetime(today.year, today.month, 1) + relativedelta(months=1, days=-1)
    except Exception as e:
        logger.error(repr(e))
    return False


def last_date_of_previous_month(today):
    """
    :param today:
    :return: last date of previous month
    """
    if not today:
        return False
    try:
        first_day = today.replace(day=1)
        return first_day - relativedelta(days=1)
    except Exception as e:
        logger.error(repr(e))
    return False

def first_date_of_this_month(today):
    if not today:
        return False
    try:
        first_of_month = today.replace(day=1)
        return first_of_month
    except Exception as e:
        logger.error(repr(e))
    return False

def last_day_of_this_month(today):
    if not today:
        return False
    try:
        last_of_this_month = ((today + relativedelta(months=1)).replace(day=1)) - relativedelta(days=1)
        return last_of_this_month
    except Exception as e:
        logger.error(repr(e))
    return False