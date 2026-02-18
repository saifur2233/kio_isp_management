import re

DIVISION_SELECTION = [
    ('dhaka', 'Dhaka (ঢাকা)'),
    ('chattogram', 'Chattogram (চট্টগ্রাম)'),
    ('rajshahi', 'Rajshahi (রাজশাহী)'),
    ('khulna', 'Khulna (খুলনা)'),
    ('barishal', 'Barishal (বরিশাল)'),
    ('sylhet', 'Sylhet (সিলেট)'),
    ('rangpur', 'Rangpur (রংপুর)'),
    ('mymensingh', 'Mymensingh (ময়মনসিংহ)'),
]

_DIVISION_DISTRICT_DATA = [
    ('dhaka', [
        ('dhaka', 'Dhaka (ঢাকা)'),
        ('gazipur', 'Gazipur (গাজীপুর)'),
        ('narayanganj', 'Narayanganj (নারায়ণগঞ্জ)'),
        ('narsingdi', 'Narsingdi (নরসিংদী)'),
        ('munshiganj', 'Munshiganj (মুন্সীগঞ্জ)'),
        ('manikganj', 'Manikganj (মানিকগঞ্জ)'),
        ('tangail', 'Tangail (টাঙ্গাইল)'),
        ('kishoreganj', 'Kishoreganj (কিশোরগঞ্জ)'),
        ('faridpur', 'Faridpur (ফরিদপুর)'),
        ('gopalganj', 'Gopalganj (গোপালগঞ্জ)'),
        ('madaripur', 'Madaripur (মাদারীপুর)'),
        ('rajbari', 'Rajbari (রাজবাড়ী)'),
        ('shariatpur', 'Shariatpur (শরীয়তপুর)'),
    ]),
    ('chattogram', [
        ('chattogram', 'Chattogram (চট্টগ্রাম)'),
        ('coxsbazar', "Cox's Bazar (কক্সবাজার)"),
        ('cumilla', 'Cumilla (কুমিল্লা)'),
        ('feni', 'Feni (ফেনী)'),
        ('noakhali', 'Noakhali (নোয়াখালী)'),
        ('lakshmipur', 'Lakshmipur (লক্ষ্মীপুর)'),
        ('chandpur', 'Chandpur (চাঁদপুর)'),
        ('brahmanbaria', 'Brahmanbaria (ব্রাহ্মণবাড়িয়া)'),
        ('khagrachhari', 'Khagrachhari (খাগড়াছড়ি)'),
        ('rangamati', 'Rangamati (রাঙামাটি)'),
        ('bandarban', 'Bandarban (বান্দরবান)'),
    ]),
    ('rajshahi', [
        ('rajshahi', 'Rajshahi (রাজশাহী)'),
        ('bogura', 'Bogura (বগুড়া)'),
        ('joypurhat', 'Joypurhat (জয়পুরহাট)'),
        ('naogaon', 'Naogaon (নওগাঁ)'),
        ('natore', 'Natore (নাটোর)'),
        ('chapainawabganj', 'Chapainawabganj (চাঁপাইনবাবগঞ্জ)'),
        ('pabna', 'Pabna (পাবনা)'),
        ('sirajganj', 'Sirajganj (সিরাজগঞ্জ)'),
    ]),
    ('khulna', [
        ('khulna', 'Khulna (খুলনা)'),
        ('bagerhat', 'Bagerhat (বাগেরহাট)'),
        ('satkhira', 'Satkhira (সাতক্ষীরা)'),
        ('jashore', 'Jashore (যশোর)'),
        ('jhenaidah', 'Jhenaidah (ঝিনাইদহ)'),
        ('magura', 'Magura (মাগুরা)'),
        ('narail', 'Narail (নড়াইল)'),
        ('kushtia', 'Kushtia (কুষ্টিয়া)'),
        ('chuadanga', 'Chuadanga (চুয়াডাঙ্গা)'),
        ('meherpur', 'Meherpur (মেহেরপুর)'),
    ]),
    ('barishal', [
        ('barishal', 'Barishal (বরিশাল)'),
        ('bhola', 'Bhola (ভোলা)'),
        ('patuakhali', 'Patuakhali (পটুয়াখালী)'),
        ('pirojpur', 'Pirojpur (পিরোজপুর)'),
        ('jhalokathi', 'Jhalokathi (ঝালকাঠি)'),
        ('barguna', 'Barguna (বরগুনা)'),
    ]),
    ('sylhet', [
        ('sylhet', 'Sylhet (সিলেট)'),
        ('moulvibazar', 'Moulvibazar (মৌলভীবাজার)'),
        ('habiganj', 'Habiganj (হবিগঞ্জ)'),
        ('sunamganj', 'Sunamganj (সুনামগঞ্জ)'),
    ]),
    ('rangpur', [
        ('rangpur', 'Rangpur (রংপুর)'),
        ('dinajpur', 'Dinajpur (দিনাজপুর)'),
        ('thakurgaon', 'Thakurgaon (ঠাকুরগাঁও)'),
        ('panchagarh', 'Panchagarh (পঞ্চগড়)'),
        ('nilphamari', 'Nilphamari (নীলফামারী)'),
        ('lalmonirhat', 'Lalmonirhat (লালমনিরহাট)'),
        ('kurigram', 'Kurigram (কুড়িগ্রাম)'),
        ('gaibandha', 'Gaibandha (গাইবান্ধা)'),
    ]),
    ('mymensingh', [
        ('mymensingh', 'Mymensingh (ময়মনসিংহ)'),
        ('jamalpur', 'Jamalpur (জামালপুর)'),
        ('sherpur', 'Sherpur (শেরপুর)'),
        ('netrokona', 'Netrokona (নেত্রকোণা)'),
    ]),
]

DISTRICT_SELECTION = [
    district
    for _, districts in _DIVISION_DISTRICT_DATA
    for district in districts
]

DISTRICT_DIVISION_MAP = {
    district_code: division_code
    for division_code, districts in _DIVISION_DISTRICT_DATA
    for district_code, _ in districts
}


def _normalize_label(label):
    return re.sub(r"[^a-z]", "", label.lower())


_DISTRICT_NAME_INDEX = {
    _normalize_label(name.split('(')[0]): code
    for code, name in DISTRICT_SELECTION
}

_DISTRICT_NAME_OVERRIDES = {
    'jhalokati': 'jhalokathi',
    'jessore': 'jashore',
}


def resolve_district_code(name):
    """Match a district name fragment to a canonical district code."""
    normalized = _normalize_label(name)
    normalized = _DISTRICT_NAME_OVERRIDES.get(normalized, normalized)
    return _DISTRICT_NAME_INDEX.get(normalized)
