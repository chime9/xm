#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import subprocess, math, os, sys, re
import config

class Listing:
    def __init__(self, num, title, obj):
        self.num = num
        self.title = title
        self.obj = obj
    
    def __str__(self):
        return "{} {}".format(self.num, self.title)

def print_out_menu_options(options):
    channel_number_set = set()
    for option in options:
        channel_number_set.add(option.num)
    full = int(math.floor(len(options) / height))
    remainder = len(options) - (full * height)

    display_control = []
    counter = 0
    for each in range(full):
        temp = []
        for itr in range(height):
            temp.append(counter)
            counter += 1

        display_control.append(temp)
    temp = []
    for each in range(remainder):
        temp.append(counter)
        counter += 1

    display_control.append(temp)

    page_itr = 0

    while True:
        os.system('clear')
        if len(options) == 0:
            print('no results found')
        for each in display_control[page_itr]:
            try:
                print(options[each].title)
            except Exception:
                pass
        result = input('choice ')
        if result == 'n':
            if page_itr < len(display_control) - 1:
                page_itr += 1
        elif result == 'p':
            if page_itr > 0:
                page_itr -= 1
        elif result == 'q':
            return None
        else:
            try:
                result = int(result)
                if result in channel_number_set:
                    for o in options:
                        if o.num == result:
                            return o
                else:
                    pass
            except ValueError:
                pass


def main_menu():
    if len(sys.argv) < 2:
        print('a filename was not supplied')
        sys.exit(1)
    channel = None
    if len(sys.argv) == 3:
        try:
            channel = int(sys.argv[2])
        except ValueError as e:
            print('channel must be a number ')
            sys.exit(1)
    options = FirefoxOptions()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    # driver = webdriver.Chrome()
    driver.get('https://player.siriusxm.com/login')
    print('waiting for sirius webpage sign in')
    WebDriverWait(driver,10).until(EC.presence_of_all_elements_located((By.ID, 'username')))

    print('logging chime into sirus website')
    user = driver.find_element_by_name('username')
    user.clear()
    user.send_keys(config.user)
    password = driver.find_element_by_name('password')
    password.clear()
    password.send_keys(config.password)
    login_button = driver.find_element_by_class_name('login-button')
    login_button.click()

    print('loading main sirius webpage')

    WebDriverWait(driver, 40).until(EC.presence_of_element_located((By.CLASS_NAME, "super-category-btn")))
    
    new_buttons = driver.find_elements_by_class_name('btn')

    choice = -1
    for i,each in enumerate(new_buttons):
        if 'all channels' in each.text.lower():
            choice = i
    if choice >= 0:
        new_buttons[choice].click()
        print('waiting for channel information')

        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "center-column")))
        time.sleep(20)
        

        listings = driver.find_elements_by_class_name('center-column')
        display_listings = []
        for listing in listings:
            listing_obj = listing.text.replace('\n',' - ')
            new_line =  listing_obj.replace(r'Ch ', '')
            res = re.findall(r'^[0-9]+', new_line)
            if res:
                display_listings.append( Listing(int(res[0]),listing_obj, listing) )

        chosen_channel = None
        if (channel is not None):
            for each in display_listings:
                if (each.num == channel):
                    chosen_channel = each
        else:
            chosen_channel = print_out_menu_options(display_listings)


        if (chosen_channel is not None):
            subprocess.call(['pulseaudio','-D','--exit-idle-time=-1'])
            subprocess.call(['pacmd','load-module','module-virtual-sink','sink_name=v1'])
            subprocess.call(['pacmd','set-default-sink','v1'])
            subprocess.call(['pacmd','set-default-source','v1.monitor'])
            chosen_channel.obj.click()
            print('starting to record {}'.format(sys.argv[1]))
            subprocess.call(['ffmpeg','-loglevel','error','-f','pulse','-i','default', '/sound/{}'.format(sys.argv[1])])
            print('recording of {} stopped'.format(sys.argv[1]))
        else:
            print('channel not found')
        


width = int(subprocess.check_output(['tput', 'cols']))
height = int(subprocess.check_output(['tput', 'lines'])) - 1

main_menu()
