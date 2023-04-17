from googletrans import Translator



def translate_injury(injury):
    """
    Function that translates an injury from English to Dutch
    From dictionary with injuries that often occur; else translation by google translate
    :param injury: string with injury in English
    :return: string with injury in Dutch
    """

    translator = Translator()
    
    injuries = {"achilles tendon rupture": "gescheurde achillespees",
    "ankle/foot injury": "enkelblessure",
    "foot injury": "voetblessure",
    "hamstring": "hamstringblessure",
    "illness": "ziek",
    "knee injury": "knieblessure",
    "knock": "knock blessure",
    "thigh muscle strain": "verrekte dijspier",
    "calf/shin injury": "scheen- of kuitblessure",
    "groin strain": "verrekte lies",
    "groin/pelvis injury": "liesblessure",
    "neck injury": "nekblessure",
    "mcl knee ligament injury": "knieligamentblessure",
    "ankle ligaments": "enkelligamentblessure",
    "arm injury": "armblessure",
    "shoulder injury": "schouderblessure",
    "concussion": "hersenschudding"}

    try:
        translation = injuries[injury.lower()]
        return translation
    
    except (KeyError):
        result = translator.translate(injury, src='en', dest='nl')
        return result.text
    
