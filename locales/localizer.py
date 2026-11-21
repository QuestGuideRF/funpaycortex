from typing import Literal
from locales import ru ,en ,uk
import logging
logger =logging .getLogger ("localizer")
class Localizer :
    def __new__ (cls ,curr_lang :str |None =None ):
        if not hasattr (cls ,"instance"):
            cls .instance =super (Localizer ,cls ).__new__ (cls )
            cls .instance .languages ={
            "ru":ru ,
            "en":en ,
            "uk":uk
            }
            cls .instance .current_language ="ru"
        if curr_lang in cls .instance .languages :
            cls .instance .current_language =curr_lang
        return cls .instance
    def _get_translation (self ,variable_name :str ,language :str ):
        lang_module =self .languages .get (language )
        if lang_module and hasattr (lang_module ,variable_name ):
            return getattr (lang_module ,variable_name )
        return None
    def translate (self ,variable_name :str ,*args ,**kwargs ):
        language =kwargs .pop ('language',None )
        text =None
        if language :
            text =self ._get_translation (variable_name ,language )
        if text is None :
            text =self ._get_translation (variable_name ,self .current_language )
        if text is None :
            text =self ._get_translation (variable_name ,"ru")
        if text is None :
            text =variable_name
        try :
            return text .format (*args ,**kwargs )
        except (IndexError ,KeyError )as e :
            logger .debug (f"Ошибка форматирования для переменной '{variable_name }' с текстом '{text }' и аргументами {args }, {kwargs }: {e }",exc_info =True )
            return text
    def add_translation (self ,uuid :str ,variable_name :str ,value :str ,language :Literal ["uk","ru","en"]):
        setattr (self .languages [language ],f"{uuid }_{variable_name }",value )
    def plugin_translate (self ,uuid :str ,variable_name :str ,*args ,**kwargs ):
        prefixed_variable_name =f"{uuid }_{variable_name }"
        language =kwargs .get ('language')
        translation =self .translate (prefixed_variable_name ,*args ,**kwargs )
        if translation ==prefixed_variable_name :
            return self .translate (variable_name ,*args ,**kwargs )
        return translation