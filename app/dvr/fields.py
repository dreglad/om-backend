from recurrence.fields import RecurrenceField as RecurrenceFieldBase


class RecurrenceField(RecurrenceFieldBase):
    """Override fix for Django 2.0"""

    def value_to_string(self, obj):
        return self.value_from_object(obj)
