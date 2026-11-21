import configparser
from configparser import ConfigParser ,SectionProxy
import codecs
import os
from Utils .exceptions import (ParamNotFoundError ,EmptyValueError ,ValueNotValidError ,SectionNotFoundError ,
ConfigParseError ,ProductsFileNotFoundError ,NoProductVarError ,
SubCommandAlreadyExists ,DuplicateSectionErrorWrapper )
from Utils .cortex_tools import hash_password
def check_param (param_name :str ,section :SectionProxy ,valid_values :list [str |None ]|None =None ,
raise_if_not_exists :bool =True )->str |None :
    if param_name not in list (section .keys ()):
        if raise_if_not_exists :
            raise ParamNotFoundError (param_name )
        return None
    value =section [param_name ].strip ()
    if not value :
        if valid_values and None in valid_values :
            return value
        raise EmptyValueError (param_name )
    if valid_values and valid_values !=[None ]and value not in valid_values :
        raise ValueNotValidError (param_name ,value ,valid_values )
    return value
def create_config_obj (config_path :str )->ConfigParser :
    config =ConfigParser (delimiters =(":",),interpolation =None )
    config .optionxform =str
    config .read_file (codecs .open (config_path ,"r","utf8"))
    return config
def load_main_config (config_path :str ):
    config =create_config_obj (config_path )
    values ={
    "FunPay":{
    "golden_key":"any",
    "user_agent":"любой+пустой",
    "autoRaise":["0","1"],
    "autoResponse":["0","1"],
    "autoDelivery":["0","1"],
    "multiDelivery":["0","1"],
    "autoRestore":["0","1"],
    "autoDisable":["0","1"],
    "oldMsgGetMode":["0","1"],
    "keepSentMessagesUnread":["0","1"],
    "locale":["ru","en","uk"]
    },
    "Telegram":{
    "enabled":["0","1"],
    "token":"любой+пустой",
    "secretKeyHash":"any",
    "blockLogin":["0","1"]
    },
    "Manager":{
    "registration_key":"любой+пустой"
    },
    "ManagerPermissions":{
    "can_view_stats":["0","1"],
    "can_edit_ar":["0","1"],
    "can_edit_ad":["0","1"],
    "can_edit_templates":["0","1"],
    "can_control_orders":["0","1"]
    },
    "BlockList":{
    "blockDelivery":["0","1"],
    "blockResponse":["0","1"],
    "blockNewMessageNotification":["0","1"],
    "blockNewOrderNotification":["0","1"],
    "blockCommandNotification":["0","1"]
    },
    "NewMessageView":{
    "includeMyMessages":["0","1"],
    "includeFPMessages":["0","1"],
    "includeBotMessages":["0","1"],
    "notifyOnlyMyMessages":["0","1"],
    "notifyOnlyFPMessages":["0","1"],
    "notifyOnlyBotMessages":["0","1"],
    "showImageName":["0","1"]
    },
    "Greetings":{
    "ignoreSystemMessages":["0","1"],
    "sendGreetings":["0","1"],
    "greetingsText":"any",
    "greetingsCooldown":"any"
    },
    "OrderConfirm":{
    "watermark":["0","1"],
    "sendReply":["0","1"],
    "replyText":"any"
    },
    "ReviewReply":{
    "star1Reply":["0","1"],
    "star2Reply":["0","1"],
    "star3Reply":["0","1"],
    "star4Reply":["0","1"],
    "star5Reply":["0","1"],
    "star1ReplyText":"любой+пустой",
    "star2ReplyText":"любой+пустой",
    "star3ReplyText":"любой+пустой",
    "star4ReplyText":"любой+пустой",
    "star5ReplyText":"любой+пустой",
    },
    "Proxy":{
    "enable":["0","1"],
    "ip":"любой+пустой",
    "port":"любой+пустой",
    "login":"любой+пустой",
    "password":"любой+пустой",
    "check":["0","1"]
    },
    "Other":{
    "watermark":"любой+пустой",
    "requestsDelay":[str (i )for i in range (1 ,101 )],
    "language":["ru","en","uk"]
    },
    "Statistics":{
    "report_interval":"any",
    "analysis_period":"any",
    },
    "OrderControl":{
    "notify_pending_execution":["0","1"],
    "pending_execution_threshold_m":"any",
    "notify_pending_confirmation":["0","1"],
    "pending_confirmation_threshold_h":"any"
    }
    }
    if "Other"not in config or "watermark"not in config ["Other"]:
        if "Other"not in config :
            config .add_section ("Other")
        config .set ("Other","watermark","🧠 𝑭𝒖𝒏𝑷𝒂𝒚 𝑪𝒐𝒓𝒕𝒆𝒙 🤖")
        with open (config_path ,"w",encoding ="utf-8")as f :
            config .write (f )
    for section_name in values :
        if section_name not in config .sections ():
            if section_name in ["Manager","ManagerPermissions","Statistics","OrderControl"]:
                config .add_section (section_name )
                if section_name =="ManagerPermissions":
                    config .set ("ManagerPermissions","can_view_stats","0")
                    config .set ("ManagerPermissions","can_edit_ar","0")
                    config .set ("ManagerPermissions","can_edit_ad","0")
                    config .set ("ManagerPermissions","can_edit_templates","0")
                    config .set ("ManagerPermissions","can_control_orders","0")
                elif section_name =="Statistics":
                    config .set ("Statistics","report_interval","0")
                    config .set ("Statistics","analysis_period","30")
                with open (config_path ,"w",encoding ="utf-8")as f :
                    config .write (f )
            else :
                raise ConfigParseError (config_path ,section_name ,SectionNotFoundError ())
        if section_name =="Greetings"and "cacheInitChats"in config [section_name ]:
            config .remove_option (section_name ,"cacheInitChats")
            with open (config_path ,"w",encoding ="utf-8")as f :
                config .write (f )
        for param_name in values [section_name ]:
            if section_name =="FunPay"and param_name =="oldMsgGetMode"and param_name not in config [section_name ]:
                config .set ("FunPay","oldMsgGetMode","0")
                with open (config_path ,"w",encoding ="utf-8")as f :
                    config .write (f )
            elif section_name =="Manager"and param_name =="registration_key"and param_name not in config [section_name ]:
                config .set ("Manager","registration_key","")
                with open (config_path ,"w",encoding ="utf-8")as f :
                    config .write (f )
            elif section_name =="ManagerPermissions"and "can_control_orders"not in config [section_name ]:
                config .set ("ManagerPermissions","can_view_stats","0")
                config .set ("ManagerPermissions","can_edit_ar","0")
                config .set ("ManagerPermissions","can_edit_ad","0")
                config .set ("ManagerPermissions","can_edit_templates","0")
                config .set ("ManagerPermissions","can_control_orders","0")
                with open (config_path ,"w",encoding ="utf-8")as f :
                    config .write (f )
            elif section_name =="Greetings"and param_name =="ignoreSystemMessages"and param_name not in config [
            section_name ]:
                config .set ("Greetings","ignoreSystemMessages","0")
                with open (config_path ,"w",encoding ="utf-8")as f :
                    config .write (f )
            elif section_name =="Other"and param_name =="language"and param_name not in config [section_name ]:
                config .set ("Other","language","ru")
                with open (config_path ,"w",encoding ="utf-8")as f :
                    config .write (f )
            elif section_name =="Other"and param_name =="language"and config [section_name ][param_name ]=="eng":
                config .set ("Other","language","en")
                with open (config_path ,"w",encoding ="utf-8")as f :
                    config .write (f )
            elif section_name =="Greetings"and param_name =="greetingsCooldown"and param_name not in config [
            section_name ]:
                config .set ("Greetings","greetingsCooldown","2")
                with open (config_path ,"w",encoding ="utf-8")as f :
                    config .write (f )
            elif section_name =="OrderConfirm"and param_name =="watermark"and param_name not in config [
            section_name ]:
                config .set ("OrderConfirm","watermark","1")
                with open (config_path ,"w",encoding ="utf-8")as f :
                    config .write (f )
            elif section_name =="FunPay"and param_name =="keepSentMessagesUnread"and param_name not in config [section_name ]:
                config .set ("FunPay","keepSentMessagesUnread","0")
                with open (config_path ,"w",encoding ="utf-8")as f :
                    config .write (f )
            elif section_name =="NewMessageView"and param_name =="showImageName"and param_name not in config [section_name ]:
                config .set ("NewMessageView","showImageName","1")
                with open (config_path ,"w",encoding ="utf-8")as f :
                    config .write (f )
            elif section_name =="Telegram"and param_name =="blockLogin"and param_name not in config [section_name ]:
                config .set ("Telegram","blockLogin","0")
                with open (config_path ,"w",encoding ="utf-8")as f :
                    config .write (f )
            elif section_name =="Telegram"and param_name =="secretKeyHash"and param_name not in config [section_name ]:
                if "secretKey"in config [section_name ]:
                    config .set (section_name ,"secretKeyHash",hash_password (config [section_name ]["secretKey"]))
                    config .remove_option (section_name ,"secretKey")
                    with open (config_path ,"w",encoding ="utf-8")as f :
                        config .write (f )
                else :
                     pass
            elif section_name =="FunPay"and param_name =="locale"and param_name not in config [section_name ]:
                config .set (section_name ,"locale","ru")
                with open (config_path ,"w",encoding ="utf-8")as f :
                    config .write (f )
            elif section_name =="Statistics"and "report_interval"not in config [section_name ]:
                config .set ("Statistics","report_interval","0")
                config .set ("Statistics","analysis_period","30")
                with open (config_path ,"w",encoding ="utf-8")as f :
                    config .write (f )
            elif section_name =="OrderControl"and "notify_pending_execution"not in config [section_name ]:
                config .set ("OrderControl","notify_pending_execution","1")
                config .set ("OrderControl","pending_execution_threshold_m","60")
                config .set ("OrderControl","notify_pending_confirmation","1")
                config .set ("OrderControl","pending_confirmation_threshold_h","24")
                with open (config_path ,"w",encoding ="utf-8")as f :
                    config .write (f )
            try :
                if values [section_name ][param_name ]=="any":
                    check_param (param_name ,config [section_name ])
                elif values [section_name ][param_name ]=="любой+пустой":
                    check_param (param_name ,config [section_name ],valid_values =[None ])
                else :
                    check_param (param_name ,config [section_name ],valid_values =values [section_name ][param_name ])
            except (ParamNotFoundError ,EmptyValueError ,ValueNotValidError )as e :
                raise ConfigParseError (config_path ,section_name ,e )
    return config
def load_auto_response_config (config_path :str ):
    try :
        config =create_config_obj (config_path )
    except configparser .DuplicateSectionError as e :
        raise ConfigParseError (config_path ,e .section ,DuplicateSectionErrorWrapper ())
    command_sets =[]
    for command in config .sections ():
        try :
            check_param ("response",config [command ])
            check_param ("telegramNotification",config [command ],valid_values =["0","1"],raise_if_not_exists =False )
            check_param ("notificationText",config [command ],raise_if_not_exists =False )
        except (ParamNotFoundError ,EmptyValueError ,ValueNotValidError )as e :
            raise ConfigParseError (config_path ,command ,e )
        if "|"in command :
            command_sets .append (command )
    for command_set in command_sets :
        commands =command_set .split ("|")
        parameters =config [command_set ]
        for new_command in commands :
            new_command =new_command .strip ()
            if not new_command :
                continue
            if new_command in config .sections ():
                raise ConfigParseError (config_path ,command_set ,SubCommandAlreadyExists (new_command ))
            config .add_section (new_command )
            for param_name in parameters :
                config .set (new_command ,param_name ,parameters [param_name ])
    return config
def load_raw_auto_response_config (config_path :str ):
    return create_config_obj (config_path )
def load_auto_delivery_config (config_path :str ):
    try :
        config =create_config_obj (config_path )
    except configparser .DuplicateSectionError as e :
        raise ConfigParseError (config_path ,e .section ,DuplicateSectionErrorWrapper ())
    for lot_title in config .sections ():
        try :
            lot_response =check_param ("response",config [lot_title ])
            products_file_name =check_param ("productsFileName",config [lot_title ],raise_if_not_exists =False )
            check_param ("disable",config [lot_title ],valid_values =["0","1"],raise_if_not_exists =False )
            check_param ("disableAutoRestore",config [lot_title ],valid_values =["0","1"],raise_if_not_exists =False )
            check_param ("disableAutoDisable",config [lot_title ],valid_values =["0","1"],raise_if_not_exists =False )
            check_param ("disableAutoDelivery",config [lot_title ],valid_values =["0","1"],raise_if_not_exists =False )
            if products_file_name is None :
                continue
        except (ParamNotFoundError ,EmptyValueError ,ValueNotValidError )as e :
            raise ConfigParseError (config_path ,lot_title ,e )
        if not os .path .exists (f"storage/products/{products_file_name }"):
            raise ConfigParseError (config_path ,lot_title ,
            ProductsFileNotFoundError (f"storage/products/{products_file_name }"))
        if "$продукт"not in lot_response :
            raise ConfigParseError (config_path ,lot_title ,NoProductVarError ())
    return config