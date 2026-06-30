import phonenumbers
import pycountry



def normalize_phone(phone):

    if not phone:
        return None

    try:
        parsed = phonenumbers.parse(phone, "IN")
        return phonenumbers.format_number(
            parsed,
            phonenumbers.PhoneNumberFormat.E164
        )

    except:
        return None


def normalize_country(country):

    if not country:
        return None

    try:
        return pycountry.countries.lookup(country).alpha_2

    except:
        return country