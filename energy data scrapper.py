from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import Select
import time
import os 
import requests
import warnings
warnings.filterwarnings("ignore")

def setDateFrom(date_from_input, driver):
    date_from = driver.find_element(By.ID, '_VisioToolbarPortlet_WAR_visioneoportlet_data_od')
    date_from.send_keys(date_from_input)
    
    select = Select(driver.find_element(By.CLASS_NAME, 'ui-datepicker-year'))
    select.select_by_value(str(int(date_from_input.split('-')[0])))
    
    # print(str(int(date_from_input.split('-')[1])-1))
    
    seelect_month = Select(driver.find_element(By.CLASS_NAME, 'ui-datepicker-month'))
    seelect_month.select_by_value(str(int(date_from_input.split('-')[1])-1))
    
    days_tab = driver.find_element(By.CLASS_NAME, 'ui-datepicker-calendar')
    select_day = days_tab.find_element(By.PARTIAL_LINK_TEXT, str(int(date_from_input.split('-')[2])))
    driver.execute_script("arguments[0].click();", select_day)
    
def setDateTo(date_to_input, driver):
    date_to = driver.find_element(By.ID, '_VisioToolbarPortlet_WAR_visioneoportlet_data_do') 
    date_to.send_keys(date_to_input)
    
    select = Select(driver.find_element(By.CLASS_NAME, 'ui-datepicker-year'))
    select.select_by_value(str(int(date_to_input.split('-')[0])))
    
    seelect_month = Select(driver.find_element(By.CLASS_NAME, 'ui-datepicker-month'))
    seelect_month.select_by_value(str(int(date_to_input.split('-')[1])-1))
    
    days_tab = driver.find_element(By.CLASS_NAME, 'ui-datepicker-calendar')
    select_day = days_tab.find_element(By.PARTIAL_LINK_TEXT, str(int(date_to_input.split('-')[2])))
    driver.execute_script("arguments[0].click();", select_day)

def skanDir(download_dir):
    dir_files_list=[]
    for root, directories, files in os.walk(download_dir):
            for filename in files:
                #print(filename)
                #filepath = os.path.join(root,filename)
                dir_files_list.append(filename)
    
    return(len(dir_files_list),dir_files_list)

def wielkosciPodstawowe(s, chrome_options, save_dir, download_dir, date_from_input, date_to_input):
    driver = webdriver.Chrome(service=s, chrome_options=chrome_options)
    driver.maximize_window()
    
    Cleantemps(download_dir)
    
    sdate = datetime.strptime(date_from_input, '%Y-%m-%d').date()
    edate = datetime.strptime(date_to_input, '%Y-%m-%d').date()
    
    date_range = [sdate+timedelta(days=x) for x in range((edate-sdate).days)]
    
    driver.get('https://www.pse.pl/dane-systemowe/funkcjonowanie-kse/raporty-dobowe-z-pracy-kse/wielkosci-podstawowe')
    ekport_za_okres = driver.find_element(By.PARTIAL_LINK_TEXT, 'Eksport za okres')
    driver.execute_script("arguments[0].click();", ekport_za_okres)
    
    start = 0
    step = 30
    end = start + step
    
    while start < len(date_range):
        
        setDateFrom(str(date_range[start]), driver)
        
        if end > len(date_range):
            setDateTo(str(date_range[-1]), driver)
        else:
            setDateTo(str(date_range[end]), driver)
        
        b4d = skanDir(download_dir)[0]
        ekport_do_csv = driver.find_element(By.PARTIAL_LINK_TEXT, 'Eksport do CSV')
        driver.execute_script("arguments[0].click();", ekport_do_csv)
        
        while(b4d==skanDir(download_dir)[0]):
            time.sleep(5)
            
        start = start + step
        end = end + step 
        print("x")
    
    # wczytanie csv i generowanie raportow
    # download_dir = r'C:\Pythonscripts\scrapper\download'
    df_pl_wyk = pd.DataFrame()
    for repos in skanDir(download_dir)[1]:
        if repos[0:6] =='PL_WYK':
            print(download_dir + '\\' + repos)
            temp_df_pl_gen = pd.read_csv(download_dir + '\\' + repos, 
                                         encoding = 'unicode_escape', sep = ';')
            df_pl_wyk = pd.concat([df_pl_wyk,temp_df_pl_gen])
    
    ## Data transform
    df_pl_wyk = df_pl_wyk.reset_index(drop=True) 
    cols_replace = df_pl_wyk.columns[2::]
    for ac in cols_replace: 
        df_pl_wyk[ac] = df_pl_wyk[ac].str.replace(',', '.').astype(float)
    
    df_pl_wyk.rename(columns={'Krajowe zapotrzebowanie na moc':'Krajowe zapotrzebowanie na moc [MW]',
                         'Sumaryczna generacja JWCD':'Sumaryczna generacja JWCD [MWh]', 
                         'Sumaryczna generacja nJWCD':'Sumaryczna generacja nJWCD',
                         'Krajowe saldo wymiany miêdzysystemowej równoleg³ej':'Krajowe saldo wymiany międzysystemowej równoległej [MWh]',
                         'Krajowe saldo wymiany miêdzysystemowej nierównoleg³ej':'Krajowe saldo wymiany międzysystemowej nierównoległej [MWh]',}, 
                 inplace=True)                                                
    
    now = datetime.now()
    today=now.strftime("%d%m%Y_%H%M%S")                                                            
    df_pl_wyk.to_excel(save_dir + '\PL_WYK_KSE'+today+'.xlsx', index=False)
    
    driver.close()

def GeneracjaMocyJW(s, chrome_options, save_dir, download_dir, date_from_input, date_to_input):
    driver = webdriver.Chrome(service=s, chrome_options=chrome_options)
    driver.maximize_window()
    
    Cleantemps(download_dir)
    
    sdate = datetime.strptime(date_from_input, '%Y-%m-%d').date()
    edate = datetime.strptime(date_to_input, '%Y-%m-%d').date()
    
    date_range = [sdate+timedelta(days=x) for x in range((edate-sdate).days)]
    
    driver.get('https://www.pse.pl/dane-systemowe/funkcjonowanie-kse/raporty-dobowe-z-pracy-kse/generacja-mocy-jednostek-wytworczych')
    ekport_za_okres = driver.find_element(By.PARTIAL_LINK_TEXT, 'Eksport za okres')
    driver.execute_script("arguments[0].click();", ekport_za_okres)
    
    
    start = 0
    step = 30
    end = start + step
    
    while start < len(date_range):
        
        setDateFrom(str(date_range[start]), driver)
        
        if end > len(date_range):
            setDateTo(str(date_range[-1]), driver)
        else:
            setDateTo(str(date_range[end]), driver)
        
        b4d = skanDir(download_dir)[0]
        ekport_do_csv = driver.find_element(By.PARTIAL_LINK_TEXT, 'Eksport do CSV')
        driver.execute_script("arguments[0].click();", ekport_do_csv)
        
        while(b4d==skanDir(download_dir)[0]):
            time.sleep(10)
            
    
        start = start + step
        end = end + step 
        print("x")
    
    #wczytanie csv i generowanie raportow
    # download_dir = r'C:\Pythonscripts\scrapper\download'
    df_pl_gen = pd.DataFrame()
    for repos in skanDir(download_dir)[1]:
        if repos[0:6] =='PL_GEN':
            print(download_dir + '\\' + repos)
            temp_df_pl_gen = pd.read_csv(download_dir + '\\' + repos, 
                                         encoding = 'unicode_escape', sep = ';')
            df_pl_gen = pd.concat([df_pl_gen,temp_df_pl_gen])
    
    ## Data transform
    df_pl_gen = df_pl_gen.reset_index(drop=True)
    for i in range(0,len(df_pl_gen)):
        print(i)
        df_pl_gen.loc[i,'Nazwa'] = df_pl_gen.loc[i,'Nazwa'].replace('³',
                                                        'ł').replace('£ód', 
                                                        'Łódź').replace('£',
                                                        'Ł').replace('ê',
                                                        'ę').replace('¹',
                                                        'ą'). replace('¯','Ż')
                                                                     
        df_pl_gen.loc[i,'Doba'] = str(datetime.strptime(str(df_pl_gen.loc[i,
                                                        'Doba']).replace('-',''),
                                                        '%Y%m%d').date())
        
        df_pl_gen.loc[i,'Data publikacji'] = str(datetime.strptime(str(df_pl_gen.loc[i,
                                                        'Data publikacji']),'%Y%m%d%H%M%S'))
        
    cols_replace = [str(item) for item in range(1, 24)]
    for ac in cols_replace:
        df_pl_gen[ac] = df_pl_gen[ac].str.replace(',', '.').astype(float)
    
    df_pl_gen.rename(columns={'Kod':'Jednostka Wytwórcza: Kod',
                         'Nazwa':'Jednostka Wytwórcza: Nazwa', 
                         '1':'Godzina 1/Wolumen',
                         '2':'Godzina 2/Wolumen',
                         '3':'Godzina 3/Wolumen',
                         '4':'Godzina 4/Wolumen',
                         '5':'Godzina 5/Wolumen',
                         '6':'Godzina 6/Wolumen',
                         '7':'Godzina 7/Wolumen',
                         '8':'Godzina 8/Wolumen',
                         '9':'Godzina 9/Wolumen',
                         '10':'Godzina 10/Wolumen',
                         '11':'Godzina 11/Wolumen',
                         '12':'Godzina 12/Wolumen',
                         '13':'Godzina 13/Wolumen',
                         '14':'Godzina 14/Wolumen',
                         '15':'Godzina 15/Wolumen',
                         '16':'Godzina 16/Wolumen',
                         '17':'Godzina 17/Wolumen',
                         '18':'Godzina 18/Wolumen',
                         '19':'Godzina 19/Wolumen',
                         '20':'Godzina 20/Wolumen',
                         '21':'Godzina 21/Wolumen',
                         '22':'Godzina 22/Wolumen',
                         '23':'Godzina 23/Wolumen',
                         '24':'Godzina 24/Wolumen',}, 
                 inplace=True)                                                 
    
    now = datetime.now()
    today=now.strftime("%d%m%Y_%H%M%S")                                                       
    df_pl_gen.to_excel(save_dir + '\PL_GEN_MOC_JW_'+today+'.xlsx', index=False)
    
    driver.close()
    
def TgeNextDayMarket(save_dir, date_from_input_tge, date_to_input_tge):
    
    sdate = datetime.strptime(date_from_input_tge, '%Y-%m-%d').date()
    edate = datetime.strptime(date_to_input_tge, '%Y-%m-%d').date()
    
    date_range_tge = [sdate+timedelta(days=x) for x in range((edate-sdate).days)]
    df_tge_out = pd.DataFrame()
    
    for date in date_range_tge:
        day = str(int(str(date).split('-')[2]))
        month = str(int(str(date).split('-')[1]))
        year = str(int(str(date).split('-')[0]))
        url_date = day + '-' + month + '-' + year
        page = requests.get('https://tge.pl/energia-elektryczna-rdn?dateShow='+ url_date +'&dateAction=')
        soup = BeautifulSoup(page.content, 'html.parser')  
        table = soup.find_all('table')
        temp_df = pd.read_html(str(table))[2]
        temp_df2 = temp_df[0:len(temp_df)-3]
        temp_df2['date'] = url_date
        df_tge_out = pd.concat([df_tge_out,temp_df2])
        
        time.sleep(2)
    
    df_tge_fin = pd.DataFrame()
    df_tge_fin['Data'] = df_tge_out[('date','')]
    df_tge_fin['Czas'] = df_tge_out['Unnamed: 0_level_0']
    df_tge_fin['FIXING I: Kurs (PLN/MWh)'] = df_tge_out.iloc[:, 1]
    df_tge_fin['FIXING I: Wolumen (MWh)'] = df_tge_out.iloc[:, 2]
    df_tge_fin['FIXING II: Kurs (PLN/MWh)'] = df_tge_out.iloc[:, 3]
    df_tge_fin['FIXING II: Wolumen (MWh)'] = df_tge_out.iloc[:, 4]
    df_tge_fin['Notowania ciągłe: Kurs (PLN/MWh)'] = df_tge_out.iloc[:, 5]
    df_tge_fin['Notowania ciągłe: Wolumen (MWh)'] = df_tge_out.iloc[:, 6]
    
    df_tge_fin = df_tge_fin.reset_index(drop=True) 
    
    cols_replace = list(df_tge_fin.columns[i] for i in [3,5,6,7])
    for ac in cols_replace:
        df_tge_fin[ac] = df_tge_fin[ac].str.replace('-', '0').astype(float)
        
    
    now = datetime.now()
    today=now.strftime("%d%m%Y_%H%M%S")                                                          
    df_tge_fin.to_excel(save_dir + '\TGE_rynek_energia_dnia_nastepnego_'+today+'.xlsx', index=False)
    
def Cleantemps(directory_cm):
    for root, directories, files in os.walk(directory_cm):
            for filename in files:
                #print(filename)
                filepath = os.path.join(root,filename)
                #file_paths.append(filepath)
                try:
                    os.remove(filepath)
                except (PermissionError, FileNotFoundError) as e:
                    print(e)
                    continue


if __name__ == '__main__':
    s = Service(ChromeDriverManager().install())
    chrome_options = Options()
    chrome_options.add_argument('headless')
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument('disable-avfoundation-overlays')
    chrome_options.add_argument('disable-internal-flash')
    chrome_options.add_argument('no-proxy-server')
    chrome_options.add_argument("disable-notifications")
    chrome_options.add_argument("disable-popup")
    prefs = {'download.default_directory' : 'C:\Pythonscripts\scrapper\download'}
    chrome_options.add_experimental_option('prefs', prefs)
    
    
    print("Wybierz jedną z opcji:")
    print("1. Generuj raport: Praca KSE- Generacja mocy Jednostek Wytwórczych")
    print("2. Generuj raport: Praca KSE - wielkości podstawowe")
    print("3. Generuj raport: TGE - Kontrakty Godzinowe")
    print("4 lub jakikolwik inny input: Zakończ")
    
    option = input("(1/2/3/4)")
    
    ok_dir = 0
    while ok_dir == 0:
        print("Wybierz lokalizację gdzie chcesz zapisać raport")
        save_dir = input("wpisz cieżkę:")
        if not os.path.exists(save_dir):
            print("nie znaleziono podanego folderu, sproboj ponownie")
            ok_dir = 0
        else:
            ok_dir =1
    
    download_dir = save_dir+'\\'+'download'
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    import sys
    if option == '1':
        # print('1')
        ok = 0
        while ok == 0:
            date_from_input = input("Podaj datę poczatkową w formacie YYYY-MM-DD:")
            date_to_input = input("Podaj datę końcową w formacie YYYY-MM-DD:")
            try:
                sdate = datetime.strptime(date_from_input, '%Y-%m-%d').date()
                edate = datetime.strptime(date_to_input, '%Y-%m-%d').date()
                if sdate >= edate:
                    print('data poczatkowa powinna by mniejsza od koncowej')
                    ok = 0
                else:
                    ok = 1
            except ValueError:
                print('Jedna z wprowadzoych dat nie odpowiada formatowi YYYY-MM-DD')
                ok = 0
        GeneracjaMocyJW(s, chrome_options, save_dir, download_dir, date_from_input, date_to_input)
        
    elif option == '2':
        # print('2')
        ok = 0
        while ok == 0:
            date_from_input = input("Podaj datę poczatkową w formacie YYYY-MM-DD:")
            date_to_input = input("Podaj datę końcową w formacie YYYY-MM-DD:")
            try:
                sdate = datetime.strptime(date_from_input, '%Y-%m-%d').date()
                edate = datetime.strptime(date_to_input, '%Y-%m-%d').date()
                if sdate >= edate:
                    print('data poczatkowa powinna by mniejsza od koncowej')
                    ok = 0
                else:
                    ok = 1
            except ValueError:
                print('Jedna z wprowadzoych dat nie odpowiada formatowi YYYY-MM-DD')
                ok = 0
        wielkosciPodstawowe(s, chrome_options, save_dir, download_dir, date_from_input, date_to_input)
    
    elif option == '3':
        # print('3')
        print('TGE posiada dane tylko 2 miesiace w tyl')
        print('Daty poczatkowa i koncowa podaj nie starsze niz 2 miesiace')
        now = datetime.now().date()
        
        ok = 0
        while ok == 0:
            
            date_from_input_tge = input("Podaj datę poczatkową w formacie YYYY-MM-DD:")
            date_to_input_tge = input("Podaj datę końcową w formacie YYYY-MM-DD:")
            
            try:
                sdate = datetime.strptime(date_from_input_tge, '%Y-%m-%d').date()
                edate = datetime.strptime(date_to_input_tge, '%Y-%m-%d').date()
                if sdate >= edate:
                    print('data poczatkowa powinna by mniejsza od koncowej')
                    ok = 0
                else:
                    time_between_insertion_from = now - datetime.strptime(date_from_input_tge, '%Y-%m-%d').date()
                    time_between_insertion_to = now - datetime.strptime(date_to_input_tge, '%Y-%m-%d').date()
                    
                    if time_between_insertion_from.days>60:
                        print("Data poczatkowa jest starsza niz 2 miesiace")
                        ok = 0
                    elif time_between_insertion_to.days>60:
                        print("Data koncowa jest starsza niz 2 miesiace")
                        ok = 0
                    else:
                        ok = 1
    
            except ValueError:
                print('Jedna z wprowadzoych dat nie odpowiada formatowi YYYY-MM-DD')
                ok = 0
          
        TgeNextDayMarket(save_dir, date_from_input_tge, date_to_input_tge)
    else:
        time.sleep(2)
        print('zamykanie...')
        sys.exit()
















