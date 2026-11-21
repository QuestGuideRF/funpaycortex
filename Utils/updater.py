import time
from logging import getLogger
from locales .localizer import Localizer
import requests
import os
import zipfile
import shutil
import json
import sys
logger =getLogger ("FPC.updater")
localizer =Localizer ()
_ =localizer .translate
HEADERS ={
"accept":"приложение/vnd.github+json",
"X-GitHub-Api-Version":"2022-11-28"
}
class Release :
    def __init__ (self ,name :str ,description :str ,sources_link :str ,tag_name :str ):
        self .name =name
        self .description =description
        self .sources_link =sources_link
        self .tag_name =tag_name
def get_tags (current_tag :str )->list [str ]|None :
    try :
        page =1
        all_tags_data :list [dict ]=[]
        max_pages_to_check =5
        current_page_checked =0
        while current_page_checked <max_pages_to_check :
            url =f"https://api.github.com/repos/beedgee/FunPayCortex/tags?page={page }&per_page=100"
            response =requests .get (url ,headers =HEADERS ,timeout =10 )
            response .raise_for_status ()
            current_page_tags =response .json ()
            if not current_page_tags :
                break
            all_tags_data .extend (current_page_tags )
            if any (tag_info .get ("name")==current_tag for tag_info in current_page_tags ):
                break
            page +=1
            current_page_checked +=1
            if current_page_checked <max_pages_to_check :time .sleep (1 )
        if not all_tags_data :
            logger .warning ("Не удалось получить теги с GitHub или репозиторий не содержит тегов.")
            return None
        tag_names =[tag_info .get ("name")for tag_info in all_tags_data if tag_info .get ("name")]
        return tag_names if tag_names else None
    except requests .exceptions .RequestException as e :
        logger .error (f"Ошибка сети при получении тегов: {e }")
        logger .debug ("TRACEBACK",exc_info =True )
        return None
    except Exception as e :
        logger .error (f"Неожиданная ошибка при получении тегов: {e }")
        logger .debug ("TRACEBACK",exc_info =True )
        return None
def get_next_tag (tags :list [str ],current_tag :str )->str |None :
    if not tags :
        return None
    try :
        curr_index =tags .index (current_tag )
        if curr_index >0 :
            return tags [curr_index -1 ]
        else :
            return None
    except ValueError :
        logger .warning (f"Текущий тег '{current_tag }' не найден в списке тегов с GitHub. Возможно, используется нестандартная версия. Будет предложено обновление до последней версии.")
        return tags [0 ]
def get_releases (from_tag_exclusive :str |None ,current_version_tag :str )->list [Release ]|None :
    try :
        page =1
        all_releases_data :list [dict ]=[]
        max_pages_to_check =5
        current_page_checked =0
        found_from_tag =from_tag_exclusive is None
        while current_page_checked <max_pages_to_check :
            url =f"https://api.github.com/repos/beedgee/FunPayCortex/releases?page={page }&per_page=100"
            response =requests .get (url ,headers =HEADERS ,timeout =10 )
            response .raise_for_status ()
            current_page_releases =response .json ()
            if not current_page_releases :
                break
            all_releases_data .extend (current_page_releases )
            if from_tag_exclusive and any (rel .get ("tag_name")==from_tag_exclusive for rel in current_page_releases ):
                found_from_tag =True
            page +=1
            current_page_checked +=1
            if current_page_checked <max_pages_to_check :time .sleep (1 )
        if not all_releases_data :
            logger .info ("Не найдено релизов на GitHub.")
            return None
        releases_to_install =[]
        for rel_data in reversed (all_releases_data ):
            tag_name =rel_data .get ("tag_name")
            if not tag_name :
                continue
            if found_from_tag :
                if from_tag_exclusive and tag_name ==from_tag_exclusive :
                    continue
                if from_tag_exclusive and releases_to_install and releases_to_install [-1 ].tag_name ==from_tag_exclusive :
                    pass
                if tag_name >current_version_tag :
                    release_name =rel_data .get ("name",tag_name )
                    description =rel_data .get ("body","Нет описания.")
                    sources_link =rel_data .get ("zipball_url")
                    if sources_link :
                        releases_to_install .append (Release (release_name ,description ,sources_link ,tag_name ))
            elif tag_name ==from_tag_exclusive :
                found_from_tag =True
        return releases_to_install if releases_to_install else None
    except requests .exceptions .RequestException as e :
        logger .error (f"Ошибка сети при получении релизов: {e }")
        logger .debug ("TRACEBACK",exc_info =True )
        return None
    except Exception as e :
        logger .error (f"Неожиданная ошибка при получении релизов: {e }")
        logger .debug ("TRACEBACK",exc_info =True )
        return None
def get_new_releases (current_tag :str )->int |list [Release ]:
    logger .info (f"Проверка обновлений для текущей версии: {current_tag }...")
    tags_from_github =get_tags (current_tag )
    if tags_from_github is None :
        logger .warning ("Не удалось получить список тегов с GitHub.")
        return 1
    latest_github_tag =tags_from_github [0 ]if tags_from_github else None
    if not latest_github_tag or latest_github_tag ==current_tag :
        logger .info ("Установлена последняя версия или текущая версия новее опубликованных.")
        return 2
    releases =get_releases (current_tag ,current_tag )
    if releases is None or not releases :
        logger .info ("Не найдено новых релизов для установки.")
        return 3
    logger .info (f"Найдено {len (releases )} новых релизов для установки.")
    return releases
def download_zip (url :str )->int :
    logger .info (f"Загрузка архива обновления с {url }...")
    os .makedirs ("storage/cache",exist_ok =True )
    try :
        with requests .get (url ,stream =True ,timeout =60 )as r :
            r .raise_for_status ()
            with open ("storage/cache/update.zip",'wb')as f :
                for chunk in r .iter_content (chunk_size =8192 ):
                    f .write (chunk )
        logger .info ("Архив обновления успешно загружен.")
        return 0
    except requests .exceptions .SSLError as e :
        logger .error (f"SSL-ошибка при загрузке архива обновления: {e }. Попробую скачать без проверки сертификата.")
        logger .debug ("TRACEBACK",exc_info =True )
        try :
            with requests .get (url ,stream =True ,timeout =60 ,verify =False )as r :
                r .raise_for_status ()
                with open ("storage/cache/update.zip",'wb')as f :
                    for chunk in r .iter_content (chunk_size =8192 ):
                        f .write (chunk )
            logger .info ("Архив обновления успешно загружен (без проверки SSL).")
            return 0
        except Exception as e_no_verify :
            logger .error (f"Повторная ошибка при загрузке архива обновления (без проверки SSL): {e_no_verify }")
            return 1
    except requests .exceptions .RequestException as e :
        logger .error (f"Ошибка сети при загрузке архива обновления: {e }")
        logger .debug ("TRACEBACK",exc_info =True )
        return 1
    except Exception as e :
        logger .error (f"Неожиданная ошибка при загрузке архива обновления: {e }")
        logger .debug ("TRACEBACK",exc_info =True )
        return 1
def extract_update_archive ()->str |int :
    logger .info ("Распаковка архива обновления...")
    update_dir ="storage/cache/update/"
    try :
        if os .path .exists (update_dir ):
            shutil .rmtree (update_dir ,ignore_errors =True )
        os .makedirs (update_dir ,exist_ok =True )
        with zipfile .ZipFile ("storage/cache/update.zip","r")as zip_ref :
            extracted_folder_name =zip_ref .namelist ()[0 ].split ('/')[0 ]
            zip_ref .extractall (update_dir )
        logger .info (f"Архив успешно распакован в: {os .path .join (update_dir ,extracted_folder_name )}")
        return extracted_folder_name
    except Exception as e :
        logger .error (f"Ошибка при распаковке архива обновления: {e }")
        logger .debug ("TRACEBACK",exc_info =True )
        return 1
def zipdir (path ,zip_obj ):
    for root ,dirs ,files in os .walk (path ):
        if os .path .basename (root )=="__pycache__":
            continue
        for file in files :
            zip_obj .write (os .path .join (root ,file ),
            os .path .relpath (os .path .join (root ,file ),
            os .path .join (path ,'..')))
def create_backup ()->int :
    logger .info ("Создание резервной копии...")
    try :
        with zipfile .ZipFile ("backup.zip","w",zipfile .ZIP_DEFLATED )as zip_f :
            for folder in ["storage","configs","plugins"]:
                if os .path .exists (folder ):
                    zipdir (folder ,zip_f )
                else :
                    logger .warning (f"Папка '{folder }' для бэкапа не найдена, пропуск.")
        logger .info ("Резервная копия успешно создана: backup.zip")
        return 0
    except Exception as e :
        logger .error (f"Ошибка при создании резервной копии: {e }")
        logger .debug ("TRACEBACK",exc_info =True )
        return 1
def install_release (folder_name_from_zip :str )->int :
    logger .info (f"Установка релиза из папки: {folder_name_from_zip }...")
    release_source_path =os .path .join ("storage/cache/update",folder_name_from_zip )
    destination_path ="."
    if not os .path .exists (release_source_path ):
        logger .error (f"Папка с обновлением '{release_source_path }' не найдена.")
        return 2
    try :
        delete_json_path =os .path .join (release_source_path ,"delete.json")
        if os .path .exists (delete_json_path ):
            logger .info ("Найден delete.json, удаляю указанные файлы/папки...")
            with open (delete_json_path ,"r",encoding ="utf-8")as f :
                items_to_delete =json .load (f )
                for item_path_str in items_to_delete :
                    full_item_path =os .path .join (destination_path ,item_path_str )
                    if os .path .exists (full_item_path ):
                        if os .path .isfile (full_item_path ):
                            os .remove (full_item_path )
                            logger .info (f"Удален файл: {full_item_path }")
                        elif os .path .isdir (full_item_path ):
                            shutil .rmtree (full_item_path ,ignore_errors =True )
                            logger .info (f"Удалена папка: {full_item_path }")
                    else :
                        logger .warning (f"Файл/папка для удаления не найден: {full_item_path }")
        logger .info ("Копирование файлов обновления...")
        for item_name in os .listdir (release_source_path ):
            if item_name =="delete.json":
                continue
            source_item_full_path =os .path .join (release_source_path ,item_name )
            dest_item_full_path =os .path .join (destination_path ,item_name )
            if item_name .lower ().endswith (".exe")and getattr (sys ,'frozen',False ):
                update_exe_dir =os .path .join (destination_path ,"update")
                os .makedirs (update_exe_dir ,exist_ok =True )
                shutil .copy2 (source_item_full_path ,os .path .join (update_exe_dir ,item_name ))
                logger .info (f"Файл .exe '{item_name }' скопирован в папку 'update'. Потребуется ручная замена.")
                continue
            if os .path .isdir (source_item_full_path ):
                shutil .copytree (source_item_full_path ,dest_item_full_path ,dirs_exist_ok =True )
            else :
                shutil .copy2 (source_item_full_path ,dest_item_full_path )
        logger .info ("Файлы обновления успешно скопированы.")
        return 0
    except Exception as e :
        logger .error (f"Ошибка при установке релиза: {e }")
        logger .debug ("TRACEBACK",exc_info =True )
        return 1