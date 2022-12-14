"""Modules containing all request/response schemas."""
from marshmallow import Schema, fields


class TastePref(Schema):
    """Schema for user taste preference."""

    salty = fields.Integer()
    spicy = fields.Integer()
    sour = fields.Integer()
    sweet = fields.Integer()

class UserSchema(Schema):
    """Request schema for user."""

    username = fields.String()
    password = fields.String()
    country = fields.String()
    tastePref = fields.Nested(TastePref)

class UserResponseSchema(Schema):
    """Response schema for user."""

    class Meta:
        ordered = True

    id = fields.Integer()
    username = fields.String()
    country = fields.String()
    tastePref = fields.Method("format_preference", dump_only=True)

    def format_preference(self, user):
        return {
            'salty': user.taste_salty,
            'spicy': user.taste_spicy,
            'sour': user.taste_sour,
            'sweet': user.taste_sweet
        }

class RatingSchema(Schema):
    """Request schema for rating."""

    userId = fields.String()
    googlePlaceId = fields.String()
    rating = fields.Integer()

class RatingResponseSchema(Schema):
    """Response schema for rating."""

    class Meta:
        ordered = True

    id = fields.Integer(dump_only=True)
    user_id = fields.String(data_key="userId")
    google_place_id = fields.String(data_key="googlePlaceId")
    rating = fields.String()

class RatingPrefSchema(Schema):
    """Request schema for ratings preference."""

    googlePlaceIds = fields.List(fields.String())
    country = fields.String()
    tastePref = fields.Nested(TastePref)

class RatingPrefResponseSchema(Schema):
    """Response schema for ratings preference."""

    class Meta:
        ordered = True

    google_place_id = fields.String(data_key="googlePlaceId")
    rating = fields.String()
    country = fields.String()
    tastePref = fields.Method("format_preference", dump_only=True)

    def format_preference(self, table):
        return {
            'salty': table.salty,
            'spicy': table.spicy,
            'sour': table.sour,
            'sweet': table.sweet
        }
