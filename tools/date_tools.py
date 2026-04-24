"""
Date and time utilities
"""

from datetime import datetime, timedelta
from typing import Optional
import calendar


def get_current_date() -> str:
    """Get current date as ISO format string."""
    return datetime.now().strftime('%Y-%m-%d')


def get_current_time() -> str:
    """Get current time as ISO format string."""
    return datetime.now().strftime('%H:%M:%S')


def get_current_datetime() -> str:
    """Get current datetime as ISO format string."""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def get_timestamp() -> int:
    """Get current Unix timestamp."""
    return int(datetime.now().timestamp())


def format_date(date: datetime, format_str: str = '%Y-%m-%d') -> str:
    """Format a datetime object to string."""
    return date.strftime(format_str)


def parse_date(date_str: str, format_str: str = '%Y-%m-%d') -> datetime:
    """Parse a date string to datetime object."""
    return datetime.strptime(date_str, format_str)


def date_difference(date1: datetime, date2: datetime) -> timedelta:
    """Calculate difference between two dates."""
    return date1 - date2


def is_leap_year(year: int) -> bool:
    """Check if a year is a leap year."""
    return calendar.isleap(year)


def get_days_in_month(year: int, month: int) -> int:
    """Get number of days in a month."""
    return calendar.monthrange(year, month)[1]


def add_days(date: datetime, days: int) -> datetime:
    """Add days to a date."""
    return date + timedelta(days=days)


def subtract_days(date: datetime, days: int) -> datetime:
    """Subtract days from a date."""
    return date - timedelta(days=days)


def add_hours(date: datetime, hours: int) -> datetime:
    """Add hours to a date."""
    return date + timedelta(hours=hours)


def add_minutes(date: datetime, minutes: int) -> datetime:
    """Add minutes to a date."""
    return date + timedelta(minutes=minutes)


def get_weekday(date: datetime) -> str:
    """Get weekday name from date."""
    return date.strftime('%A')


def get_weekday_number(date: datetime) -> int:
    """Get weekday number (0=Monday, 6=Sunday)."""
    return date.weekday()


def get_week_number(date: datetime) -> int:
    """Get ISO week number."""
    return date.isocalendar()[1]


def get_month_name(month: int) -> str:
    """Get month name from number."""
    return calendar.month_name[month]


def get_month_abbr(month: int) -> str:
    """Get month abbreviation from number."""
    return calendar.month_abbr[month]


def start_of_day(date: datetime) -> datetime:
    """Get start of day (midnight)."""
    return date.replace(hour=0, minute=0, second=0, microsecond=0)


def end_of_day(date: datetime) -> datetime:
    """Get end of day (23:59:59)."""
    return date.replace(hour=23, minute=59, second=59, microsecond=999999)


def start_of_month(date: datetime) -> datetime:
    """Get first day of month."""
    return date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def end_of_month(date: datetime) -> datetime:
    """Get last day of month."""
    last_day = calendar.monthrange(date.year, date.month)[1]
    return date.replace(day=last_day, hour=23, minute=59, second=59, microsecond=999999)


def is_today(date: datetime) -> bool:
    """Check if date is today."""
    return date.date() == datetime.now().date()


def is_yesterday(date: datetime) -> bool:
    """Check if date is yesterday."""
    return date.date() == (datetime.now() - timedelta(days=1)).date()


def is_tomorrow(date: datetime) -> bool:
    """Check if date is tomorrow."""
    return date.date() == (datetime.now() + timedelta(days=1)).date()


def days_until(date: datetime) -> int:
    """Get number of days until a date."""
    delta = date - datetime.now()
    return delta.days


def business_days_between(start: datetime, end: datetime) -> int:
    """Count business days between two dates (excludes weekends)."""
    delta = end - start
    total_days = delta.days
    weekends = sum(1 for i in range(total_days + 1) 
                   if (start + timedelta(days=i)).weekday() >= 5)
    return total_days - weekends + 1


def age_from_birthdate(birthdate: datetime) -> int:
    """Calculate age from birthdate."""
    today = datetime.now()
    age = today.year - birthdate.year
    if (today.month, today.day) < (birthdate.month, birthdate.day):
        age -= 1
    return age
