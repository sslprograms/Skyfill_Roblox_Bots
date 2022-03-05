import requests, threading, json, subprocess, colorama, time, random, string, win32event, pymsgbox, pygetwindow, playsound, pyautogui, os

# username:password@ip:port

'''
=- Skyfill Multiple Feature Tool =-

Developed by sslprograms // Jake

'''

vupdate = '1.0'


subprocess.getoutput('mode con:cols=102 lines=34')
subprocess.getoutput(f'title Skyfill v{vupdate}')

config = json.loads(
    open('config//config.json', 'r').read()
)['settings']

threads = config['threading']['threads']
workers = config['threading']['workers']

cookies = open('cookies//cookies.txt', 'r').read().splitlines()
proxies = open('proxies//proxies.txt', 'r').read().splitlines()

agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 Edg/95.0.1020.44']
currentCount = 0

two_captcha_key = config['2captcha']['key']

proxyType = config['proxies']['type']
proxyFormat = config['proxies']['format']

print_queue = []
threading_queue = []

colors = {
    'green':colorama.Fore.GREEN,
    'red':colorama.Fore.RED,
    'white':colorama.Fore.WHITE,
    'blue':colorama.Fore.BLUE,
    'lblue':colorama.Fore.LIGHTBLUE_EX,
    'yellow':colorama.Fore.YELLOW,
    'magenta':colorama.Fore.MAGENTA,
    'lmagenta':colorama.Fore.LIGHTMAGENTA_EX,
    'lred':colorama.Fore.LIGHTRED_EX,
    'lyellow':colorama.Fore.LIGHTYELLOW_EX,
    'cyan':colorama.Fore.CYAN,
    'lcyan':colorama.Fore.LIGHTCYAN_EX,
    'lgreen':colorama.Fore.LIGHTGREEN_EX
}

if config['theme']['enabled'] == True:
    colorama.init()


def check_for_blocked_screens():

    blcoked = ['OBS', 'Snipping Tool']

    while True:
        try:
            time.sleep(2)

            for block in blcoked:

                screens = pygetwindow.getWindowsWithTitle(block)

                for x  in screens:

                    x.close()
                    pymsgbox.alert(text='We would like our tool private from the public, this helps prevent Roblox from patching our features.', title='Skyfill v1.0')
        except:
            pass

# threading.Thread(target=check_for_blocked_screens,).start()

success_color = colors[config['theme']['color_settings']['successColor']]
failed_color = colors[config['theme']['color_settings']['failedColor']]
idle_color = colors[config['theme']['color_settings']['idleColor']]



def print_queue_handler():

    while True:
        time.sleep(0.01)
        for __print__ in print_queue:
            
            print_queue.remove(__print__)
            print(__print__)

threading.Thread(target=print_queue_handler,).start()

# Get captcha data for 2captcha #

captcha_index = {
    'follow':f'https://friends.roblox.com/v1/users/<>/follow',
    'group':f'https://groups.roblox.com/v1/groups/<>/users',
    'cookie':f'https://auth.roblox.com/<>/signup'
}


def solveCaptcha(captchaBlob, public_key, page_url):

    requestTwoCaptcha = requests.post(
        f'http://2captcha.com/in.php',
        params = {
            'key':two_captcha_key,
            'method':'funcaptcha',
            'publickey':public_key,
            'surl':'https://roblox-api.arkoselabs.com/',
            'pageurl':page_url,
            'data[blob]':captchaBlob
        }
    )

    if requestTwoCaptcha.status_code == 200:

        KEY = requestTwoCaptcha.text.split('|')[1]
        print_queue.append(idle_color + f'> Solving FunCaptcha:{success_color} {KEY}')

        while True:

            time.sleep(10)


            checkKey = requests.get(
                f'http://2captcha.com/res.php?key={two_captcha_key}&action=get&id={KEY}'
            )

            if checkKey.text != 'CAPCHA_NOT_READY':
                token = checkKey.text.replace('OK|', '')
                return token, KEY



def get_captcha_data(cookie, proxy, type, inputId):

    with requests.session() as session:

        session.cookies['.ROBLOSECURITY'] = cookie

        if proxyFormat != 0:

            proxy_addr = proxy.split(':')

            proxy_port = proxy_addr[1]
            proxy_username = proxy_addr[2]
            proxy_password = proxy_addr[3]
            proxy_addr = proxy_addr[0]

            session.proxies = {
                'http':f'{proxyType}://' + proxy_username + ':' + proxy_password + '@' + proxy_addr + ':' + proxy_port,
                'https':f'{proxyType}://' + proxy_username + ':' + proxy_password + '@' + proxy_addr + ':' + proxy_port
            }

        elif proxyFormat == 0:

            session.proxies = {
                'http':f'{proxyType}://' + proxy,
                'https':f'{proxyType}://' + proxy
            }

        try:

            session.headers['x-csrf-token'] = session.post(
                'https://friends.roblox.com/v1/users/1/request-friendship'
            ).headers['x-csrf-token']
        
        except:

            session.headers['x-csrf-token'] = session.post(
                'https://auth.roblox.com/v2/signup'
            ).headers['x-csrf-token']

        index_url = captcha_index[type].replace('<>', inputId)
        getCaptcha = session.post(
            index_url,
            data = {
                'captchaToken':None,
                'captchaProvider':'PROVIDER_ARKOSE_LABS',
                'captchaId':None
            }
        ).json()['errors'][0]['fieldData']

        captchaId = getCaptcha.split(',\"unifiedCaptchaId\":\"')[1].split('\"}"}]}')[0].split('"}')[0].strip()
        captchaBlob = getCaptcha.split('{\"dxBlob\":\"')[1].split('\",\"unifiedCaptchaId\"')[0].strip()

    return [captchaId, captchaBlob]

        
# Cookie Checker #

def checkCookie(cookie):
    try:
        global currentCount

        timeStamp = time.time()

        with requests.session() as session:
            old_cookie = cookie

            if config['cookies']['format'] != 0:

                cookie = '_|' + cookie.split('_|')[1]
            
            session.cookies['.ROBLOSECURITY'] = cookie

            session.headers['user-agent'] = random.choice(agents)

            check_cookie = session.get(
                'https://users.roblox.com/v1/users/authenticated'
            )

            if check_cookie.status_code == 200:

                userId = check_cookie.json()['id']
                timeStamp = time.time() - timeStamp
                currentCount += 1
                output = {
                    'taskTime':timeStamp,
                    'userId':userId
                }

                open('cookiechecker//valid_cookies.txt', 'a').write(old_cookie + '\n')

                print_queue.append(idle_color + f'> Valid:{success_color} {output}')

            elif check_cookie.status_code != 200:
                open('cookiechecker//bad_cookies.txt', 'a').write(old_cookie + '\n')
                print_queue.append(idle_color + f'> Error:{failed_color} Invalid Cookie')

        
        threading_queue.remove(old_cookie)

    except Exception as error:

        print_queue.append(idle_color + f'> Error:{failed_color} {error}')
        open('cookiechecker//unchecked.txt', 'a').write(old_cookie + '\n')
        threading_queue.remove(old_cookie)
        

 
def cookie_checker_handle(inputData):
    for x in inputData:
        threading.Thread(target=checkCookie, args=(x,)).start()


def select_cookie_check():
    global currentCount

    currentCount = 0

    packet = cookies

    while True:
        time.sleep(1)

        if len(packet) == 0 and len(threading_queue) == 0:
            break 

        if len(threading_queue) <= 1:

            for x in range(threads):
                
                thread_cookies = []

                for y in range(workers):
                    
                    if len(packet) != 0:
                        cookie = random.choice(packet)
                        packet.remove(cookie)
                        thread_cookies.append(cookie)


                for ii in thread_cookies:
                    threading_queue.append(ii)

                threading.Thread(target=cookie_checker_handle, args=(thread_cookies,)).start()

    print(idle_color + f'> Task Finished, {success_color}Cookie checker..')
    input()

            

# Proxy Checker #

def checkProxy(proxy):
    try:
        global threading_queue, currentCount

        old_proxy = proxy

        timeStamp = time.time()

        with requests.session() as session:

            if proxyFormat != 0:

                proxy_addr = proxy.split(':')

                proxy_port = proxy_addr[1]
                proxy_username = proxy_addr[2]
                proxy_password = proxy_addr[3]
                proxy_addr = proxy_addr[0]

                session.proxies = {
                    'http':f'{proxyType}://' + proxy_username + ':' + proxy_password + '@' + proxy_addr + ':' + proxy_port,
                    'https':f'{proxyType}://' + proxy_username + ':' + proxy_password + '@' + proxy_addr + ':' + proxy_port
                }

            elif proxyFormat == 0:

                session.proxies = {
                    'http':f'{proxyType}://' + proxy,
                    'https':f'{proxyType}://' + proxy
                }
            

            check_proxy = session.get(
                'https://users.roblox.com'
            )

            if check_proxy.status_code == 200:

                output = {
                    'taskTime':time.time() - timeStamp,
                    'proxy':old_proxy
                }

                open('proxychecker//valid_proxies.txt', 'a').write(old_proxy + '\n')
                print_queue.append(idle_color + f'> Valid:{success_color} {output}')
                currentCount += 1
            
            else:
                print_queue.append(idle_color + f'> Error:{failed_color} Proxy blocked')
                open('proxychecker//bad_proxies.txt', 'a').write(old_proxy + '\n')

            threading_queue.remove(old_proxy)

    except Exception as error:
        threading_queue.remove(old_proxy)
        print_queue.append(idle_color + f'> Error:{failed_color} {error}')
        open('proxychecker//bad_proxies.txt', 'a').write(old_proxy + '\n')


def proxy_checker_handle(inputData):
    for x in inputData:
        threading.Thread(target=checkProxy, args=(x,)).start()


def select_proxy_check():
    global currentCount

    currentCount = 0

    packet = proxies

    while True:
        time.sleep(1)

        if len(packet) == 0 and len(threading_queue) == 0:
            break 

        if len(threading_queue) <= 1:

            for x in range(threads):
                
                thread_proxies = []

                for y in range(workers):
                    
                    if len(packet) != 0:
                        cookie = random.choice(packet)
                        packet.remove(cookie)
                        thread_proxies.append(cookie)


                for ii in thread_proxies:
                    threading_queue.append(ii)

                threading.Thread(target=proxy_checker_handle, args=(thread_proxies,)).start()
    
    print(idle_color + f'> Task Finished, {success_color}Proxy checker..')
    input()




# Description Checker

def checkDescription(cookie):
    try:
        global currentCount

        timeStamp = time.time()

        with requests.session() as session:
            old_cookie = cookie

            if config['cookies']['format'] != 0:

                cookie = '_|' + cookie.split('_|')[1]
            
            session.cookies['.ROBLOSECURITY'] = cookie

            session.headers['user-agent'] = random.choice(agents)

            check_cookie = session.get(
                'https://users.roblox.com/v1/users/authenticated'
            )

            desc = session.get(
                'https://accountinformation.roblox.com/v1/description'
            )
            if check_cookie.status_code == 200 and desc.status_code == 200:

                userName = check_cookie.json()['name']
                timeStamp = time.time() - timeStamp
                desc = desc.json()['description']

                output = {
                    'taskTime':timeStamp,
                    'userName':userName
                }

                print_queue.append(idle_color + f'> Checked:{success_color} {output}')

                output.update(
                    {
                        'description':desc
                    }
                )

                open('descriptionchecker//descriptions.txt', 'a').write(json.dumps(output) + '\n')

            currentCount += 1
        
        threading_queue.remove(old_cookie)

    except Exception as error:

        print_queue.append(idle_color + f'> Error:{failed_color} {error}')
        open('descriptionchecker//unchecked.txt', 'a').write(old_cookie + '\n')
        threading_queue.remove(old_cookie)


def cookie_description_checker_handle(inputData):
    for x in inputData:
        threading.Thread(target=checkDescription, args=(x,)).start()

def select_description_checker():
    global currentCount

    currentCount = 0

    packet = cookies

    while True:
        time.sleep(1)

        if len(packet) == 0 and len(threading_queue) == 0:
            break 

        if len(threading_queue) <= 1:

            for x in range(threads):
                
                thread_cookies = []

                for y in range(workers):
                    
                    if len(packet) != 0:
                        cookie = random.choice(packet)
                        packet.remove(cookie)
                        thread_cookies.append(cookie)


                for ii in thread_cookies:
                    threading_queue.append(ii)

                threading.Thread(target=cookie_description_checker_handle, args=(thread_cookies,)).start()

    print(idle_color + f'> Task Finished, {success_color}Description checker..')
    input()


# Friend Checker
def checkFriends(cookie):
    try:
        global currentCount

        timeStamp = time.time()

        with requests.session() as session:
            old_cookie = cookie

            if config['cookies']['format'] != 0:

                cookie = '_|' + cookie.split('_|')[1]
            
            session.cookies['.ROBLOSECURITY'] = cookie

            session.headers['user-agent'] = random.choice(agents)

            friend_count = session.get(
                'https://friends.roblox.com/v1/my/friends/count'
            ).json()['count']

            output = {
                'taskTime':time.time() - timeStamp,
                'friends':friend_count
            }

            print_queue.append(idle_color + f'> Friends checker:{success_color} {output}')

            if friend_count > 0:
                open('friendscheck//cookies_with_friends.txt', 'a').write(old_cookie+'\n')
            elif friend_count == 0:
                open('friendscheck//no_friends.txt', 'a').write(old_cookie + '\n')

        currentCount += 1
        threading_queue.remove(old_cookie)

    except Exception as error:

        print_queue.append(idle_color + f'> Error:{failed_color} {error}')
        open('friendscheck//unchecked.txt', 'a').write(old_cookie + '\n')
        threading_queue.remove(old_cookie)


def friends_checker_handle(inputData):
    for x in inputData:
        threading.Thread(target=checkFriends, args=(x,)).start()


def select_friends_checker():
    global currentCount

    currentCount = 0

    packet = cookies

    while True:
        time.sleep(1)

        if len(packet) == 0 and len(threading_queue) == 0:
            break 

        if len(threading_queue) <= 1:

            for x in range(threads):
                
                thread_cookies = []

                for y in range(workers):
                    
                    if len(packet) != 0:
                        cookie = random.choice(packet)
                        packet.remove(cookie)
                        thread_cookies.append(cookie)


                for ii in thread_cookies:
                    threading_queue.append(ii)

                threading.Thread(target=friends_checker_handle, args=(thread_cookies,)).start()

    print(idle_color + f'> Task Finished, {success_color}Friends checker..')
    input()


# Robux Checker

def checkRobux(cookie, proxy):
    try:
        global currentCount

        timeStamp = time.time()

        with requests.session() as session:
            old_cookie = cookie
            old_proxy = proxy

            if config['cookies']['format'] != 0:

                cookie = '_|' + cookie.split('_|')[1]
            
            session.cookies['.ROBLOSECURITY'] = cookie

            session.headers['user-agent'] = random.choice(agents)

            if proxyFormat != 0:

                proxy_addr = proxy.split(':')

                proxy_port = proxy_addr[1]
                proxy_username = proxy_addr[2]
                proxy_password = proxy_addr[3]
                proxy_addr = proxy_addr[0]

                session.proxies = {
                    'http':f'{proxyType}://' + proxy_username + ':' + proxy_password + '@' + proxy_addr + ':' + proxy_port,
                    'https':f'{proxyType}://' + proxy_username + ':' + proxy_password + '@' + proxy_addr + ':' + proxy_port
                }

            elif proxyFormat == 0:

                session.proxies = {
                    'http':f'{proxyType}://' + proxy,
                    'https':f'{proxyType}://' + proxy
                }

            robux = session.get(
                'https://api.roblox.com/currency/balance'
            ).json()['robux']


            output = {
                'taskTime':time.time() - timeStamp,
                'robux':robux,
                'proxy':old_proxy
            }

            print_queue.append(idle_color + f'> Robux checker:{success_color} {output}')

            if robux > 0:
                open('robuxchecker//robux_cookies.txt', 'a').write(old_cookie + '\n')
            elif robux == 0:
                open('robuxchecker//no_robux_cookies.txt', 'a').write(old_cookie + '\n')
        currentCount += 1
        threading_queue.remove(old_cookie)

    except Exception as error:
        open('robuxchecker//unchecked.txt', 'a').write(old_cookie + '\n')
        print_queue.append(idle_color + f'> Error:{failed_color} {error}')
        threading_queue.remove(old_cookie)


def robux_checker_handle(inputData):
    rotate_proxies = 0
    for x in inputData:
        threading.Thread(target=checkRobux, args=(x,proxies[rotate_proxies],)).start()
        rotate_proxies += 1

    if rotate_proxies >= len(proxies):
        rotate_proxies = 0

def select_robux_checker():
    global currentCount

    currentCount = 0

    packet = cookies

    while True:
        time.sleep(1)

        if len(packet) == 0 and len(threading_queue) == 0:
            break 

        if len(threading_queue) <= 1:

            for x in range(threads):
                
                thread_cookies = []

                for y in range(workers):
                    
                    if len(packet) != 0:
                        cookie = random.choice(packet)
                        packet.remove(cookie)
                        thread_cookies.append(cookie)


                for ii in thread_cookies:
                    threading_queue.append(ii)

                threading.Thread(target=robux_checker_handle, args=(thread_cookies,)).start()

    print(idle_color + f'> Task Finished, {success_color}Robux checker..')
    input()


# Verified Checker

def checkVerified(cookie, proxy):
    try:
        global currentCount

        timeStamp = time.time()

        with requests.session() as session:
            old_cookie = cookie
            old_proxy = proxy

            if config['cookies']['format'] != 0:

                cookie = '_|' + cookie.split('_|')[1]
            
            session.cookies['.ROBLOSECURITY'] = cookie

            session.headers['user-agent'] = random.choice(agents)

            if proxyFormat != 0:

                proxy_addr = proxy.split(':')

                proxy_port = proxy_addr[1]
                proxy_username = proxy_addr[2]
                proxy_password = proxy_addr[3]
                proxy_addr = proxy_addr[0]

                session.proxies = {
                    'http':f'{proxyType}://' + proxy_username + ':' + proxy_password + '@' + proxy_addr + ':' + proxy_port,
                    'https':f'{proxyType}://' + proxy_username + ':' + proxy_password + '@' + proxy_addr + ':' + proxy_port
                }

            elif proxyFormat == 0:

                session.proxies = {
                    'http':f'{proxyType}://' + proxy,
                    'https':f'{proxyType}://' + proxy
                }

            email = session.get(
                'https://accountsettings.roblox.com/v1/email'
            )


            output = {
                'taskTime':time.time() - timeStamp,
                'verified':email.json()['verified'],
                'proxy':old_proxy
            }

            print_queue.append(idle_color + f'> Verified checker:{success_color} {output}')

            if email.json()['verified'] == True:
                open('verifiedchecker//verified_cookies.txt', 'a').write(old_cookie + '\n')
            elif email.json()['verified'] == False:
                open('verifiedchecker//not_verified.txt', 'a').write(old_cookie + '\n')
        currentCount += 1
        threading_queue.remove(old_cookie)

    except Exception as error:
        threading_queue.remove(old_cookie)
        open('verifiedchecker//unchecked.txt', 'a').write(old_cookie + '\n')
        print_queue.append(idle_color + f'> Error:{failed_color} {error}')


def verified_checker_handle(inputData):
    rotate_proxies = 0
    for x in inputData:
        threading.Thread(target=checkVerified, args=(x,proxies[rotate_proxies],)).start()
        rotate_proxies += 1

    if rotate_proxies >= len(proxies):
        rotate_proxies = 0


def select_verified_checker():
    global currentCount

    currentCount = 0

    packet = cookies

    while True:
        time.sleep(1)

        if len(packet) == 0 and len(threading_queue) == 0:
            break 

        if len(threading_queue) <= 1:

            for x in range(threads):
                
                thread_cookies = []

                for y in range(workers):
                    
                    if len(packet) != 0:
                        cookie = random.choice(packet)
                        packet.remove(cookie)
                        thread_cookies.append(cookie)


                for ii in thread_cookies:
                    threading_queue.append(ii)

                threading.Thread(target=verified_checker_handle, args=(thread_cookies,)).start()

    print(idle_color + f'> Task Finished, {success_color}Verified checker..')
    input()


# Follow Bot
def sendFollow(cookie, userIds, proxy):
    try:
        global currentCount
        
        for userId in userIds:

            timeStamp = time.time()


            with requests.session() as session:
                old_cookie = cookie
                old_proxy = proxy

                if config['cookies']['format'] != 0:

                    cookie = '_|' + cookie.split('_|')[1]
                
                session.cookies['.ROBLOSECURITY'] = cookie

                session.headers['user-agent'] = random.choice(agents)

                if proxyFormat != 0:

                    proxy_addr = proxy.split(':')

                    proxy_port = proxy_addr[1]
                    proxy_username = proxy_addr[2]
                    proxy_password = proxy_addr[3]
                    proxy_addr = proxy_addr[0]

                    session.proxies = {
                        'http':f'{proxyType}://' + proxy_username + ':' + proxy_password + '@' + proxy_addr + ':' + proxy_port,
                        'https':f'{proxyType}://' + proxy_username + ':' + proxy_password + '@' + proxy_addr + ':' + proxy_port
                    }

                elif proxyFormat == 0:

                    session.proxies = {
                        'http':f'{proxyType}://' + proxy,
                        'https':f'{proxyType}://' + proxy
                    }

                captcha = get_captcha_data(cookie, proxy, 'follow', userId)

                captchaBlob = captcha[1]
                captchaId = captcha[0]
    
                token, taskId = solveCaptcha(captchaBlob, '63E4117F-E727-42B4-6DAA-C8448E9B137F', f'https://www.roblox.com/users/{userId}/profile')
                

                session.headers['x-csrf-token'] = session.post(
                    'https://friends.roblox.com/v1/users/1/request-friendship'
                ).headers['x-csrf-token']

                followUser = session.post(
                    f'https://friends.roblox.com/v1/users/{userId}/follow',

                    data = {
                        'captchaId':captchaId,
                        'captchaProvider':'PROVIDER_ARKOSE_LABS',
                        'captchaToken':token
                    }
                )


                output = {
                    'taskTime':time.time() - timeStamp,
                    'proxy':proxy,
                    'target':userId
                }


                if followUser.status_code == 200:
                    requests.post(
                        f'http://2captcha.com/res.php?key={two_captcha_key}&action=reporgood&id={taskId}'
                    )
                    print_queue.append(idle_color + f'> Sent Follow:{success_color} {output}')
                
                elif followUser.status_code != 200:
                    requests.post(
                        f'http://2captcha.com/res.php?key={two_captcha_key}&action=reportbad&id={taskId}'
                    )
                    print_queue.append(idle_color + f'> Error:{failed_color} Captcha failed')

        currentCount += 1
        threading_queue.remove(old_cookie)

    except Exception as error:
        threading_queue.remove(old_cookie)
        print_queue.append(idle_color + f'> Error:{failed_color} {error}')


def follow_bot_handle(inputData, userId):
    rotate_proxies = 0
    for x in inputData:
        threading.Thread(target=sendFollow, args=(x,userId,proxies[rotate_proxies],)).start()
        rotate_proxies += 1

    if rotate_proxies >= len(proxies):
        rotate_proxies = 0


def select_follow_bot():
    global currentCount, threading_queue, print_queue

    print(idle_color + '> If you have multiple userIds seperate each one with ","')
    print(idle_color + f'> Enter UserId(s):')
    userId = input('-: ')

    if userId.count(',') == 0:

        userId = [userId]
    
    elif userId.count(',') > 0:

        userId = userId.split(',')

    currentCount = 0
    packet = []
    round = 0

    for x in cookies:
        packet.append(x)
        round += 1

    while True:
        time.sleep(1)

        if len(packet) == 0 and len(threading_queue) == 0:
            break 

        if len(threading_queue) <= 1:

            for x in range(threads):
                
                thread_cookies = []

                for y in range(workers):
                    
                    if len(packet) != 0:
                        cookie = random.choice(packet)
                        packet.remove(cookie)
                        thread_cookies.append(cookie)


                for ii in thread_cookies:

                    threading_queue.append(ii)

                threading.Thread(target=follow_bot_handle, args=(thread_cookies,userId,)).start()

    print(idle_color + f'> Task Finished, {success_color}Follow bot..')
    input()


# Friend Bot

def sendFriend(cookie, userIds):
    try:
        global currentCount
        
        for userId in userIds:

            timeStamp = time.time()


            with requests.session() as session:
                old_cookie = cookie

                if config['cookies']['format'] != 0:

                    cookie = '_|' + cookie.split('_|')[1]
                
                session.cookies['.ROBLOSECURITY'] = cookie

                session.headers['user-agent'] = random.choice(agents)
                

                session.headers['x-csrf-token'] = session.post(
                    'https://friends.roblox.com/v1/users/1/request-friendship'
                ).headers['x-csrf-token']


                send_request = session.post(
                    f'https://friends.roblox.com/v1/users/{userId}/request-friendship'
                )

                output = {
                    'taskTime':time.time() - timeStamp,
                    'target':userId
                }


                if send_request.status_code == 200:
                    print_queue.append(idle_color + f'> Sent Request:{success_color} {output}')
                
                elif send_request.status_code != 200:
                    print_queue.append(idle_color + f'> Error:{failed_color} Request blocked')

        currentCount += 1
        threading_queue.remove(old_cookie)

    except Exception as error:
        threading_queue.remove(old_cookie)
        print_queue.append(idle_color + f'> Error:{failed_color} {error}')


def friend_bot_handle(inputData, userId):
    rotate_proxies = 0
    for x in inputData:
        threading.Thread(target=sendFriend, args=(x,userId,)).start()
        rotate_proxies += 1

    if rotate_proxies >= len(proxies):
        rotate_proxies = 0


def select_friend_bot():
    global currentCount, threading_queue, print_queue

    print(idle_color + '> Enter Amount: ')
    amount = input('-: ')

    print(idle_color + '> If you have multiple userIds seperate each one with ","')
    print(idle_color + f'> Enter UserId(s):')
    userId = input('-: ')

    if userId.count(',') == 0:

        userId = [userId]
    
    elif userId.count(',') > 0:

        userId = userId.split(',')

    currentCount = 0
    packet = []
    round = 0

    for x in cookies:
        packet.append(x)
        round += 1

        if round >= int(amount):
            break

    while True:
        time.sleep(1)

        if len(packet) == 0 and len(threading_queue) == 0:
            break 

        if len(threading_queue) <= 1:

            for x in range(threads):
                
                thread_cookies = []

                for y in range(workers):
                    
                    if len(packet) != 0:
                        cookie = random.choice(packet)
                        packet.remove(cookie)
                        thread_cookies.append(cookie)


                for ii in thread_cookies:

                    threading_queue.append(ii)

                threading.Thread(target=friend_bot_handle, args=(thread_cookies,userId,)).start()

    print(idle_color + f'> Task Finished, {success_color}Friend request bot..')
    input()


# Report botter

def sendReport(cookie, userIds, proxy):
    try:
        global currentCount
        
        for userId in userIds:

            timeStamp = time.time()


            with requests.session() as session:
                old_cookie = cookie

                if proxyFormat != 0:

                    proxy_addr = proxy.split(':')

                    proxy_port = proxy_addr[1]
                    proxy_username = proxy_addr[2]
                    proxy_password = proxy_addr[3]
                    proxy_addr = proxy_addr[0]

                    session.proxies = {
                        'http':f'{proxyType}://' + proxy_username + ':' + proxy_password + '@' + proxy_addr + ':' + proxy_port,
                        'https':f'{proxyType}://' + proxy_username + ':' + proxy_password + '@' + proxy_addr + ':' + proxy_port
                    }

                elif proxyFormat == 0:

                    session.proxies = {
                        'http':f'{proxyType}://' + proxy,
                        'https':f'{proxyType}://' + proxy
                    }

                if config['cookies']['format'] != 0:

                    cookie = '_|' + cookie.split('_|')[1]
                
                session.cookies['.ROBLOSECURITY'] = cookie


                session.headers['user-agent'] = random.choice(agents)

                session.headers['referer'] = f'https://www.roblox.com/abusereport/userprofile?id={userId}'
                session.headers['origin'] = 'https://www.roblox.com'

                __RequestVerificationToken =  session.get(f'https://www.roblox.com/abusereport/userprofile?id={userId}').text.split('<input name="__RequestVerificationToken" type="hidden" value="')[1].split('" />')[0]

                send_report = session.post(
                    f'https://www.roblox.com/abusereport/userprofile?id={userId}',

                    data = {
                        '__RequestVerificationToken':__RequestVerificationToken,
                        'ReportCategory':6,
                        'Comment':'',
                        'Id':userId,
                        'RedirectUrl':f'https://www.roblox.com/abusereport/userprofile?id={userId}',
                        'PartyGuid':'',
                        'ConversationId':''
                    }
                )

                output = {
                    'taskTime':time.time() - timeStamp,
                    'target':userId,
                    'proxy':proxy
                }


                if send_report.status_code == 200 or send_report.status_code == 302:
                    print_queue.append(idle_color + f'> Sent Report:{success_color} {output}')
                
                elif send_report.status_code != 200 and send_report.status_code != 302:
                    print_queue.append(idle_color + f'> Error:{failed_color} Request blocked')

        currentCount += 1
        threading_queue.remove(old_cookie)

    except Exception as error:
        threading_queue.remove(old_cookie)
        print_queue.append(idle_color + f'> Error:{failed_color} {error}')

def report_botter_handle(inputData, userIds):
    rotate_proxies = 0
    for x in inputData:
        threading.Thread(target=sendReport, args=(x,userIds,proxies[rotate_proxies],)).start()
        rotate_proxies += 1

    if rotate_proxies >= len(proxies):
        rotate_proxies = 0


def select_report_botter():
    global currentCount

    currentCount = 0

    packet = cookies

    print(idle_color + '> Enter Amount: ')
    amount = input('-: ')

    print(idle_color + '> If you have multiple userIds seperate each one with ","')
    print(idle_color + f'> Enter UserId(s):')
    userId = input('-: ')

    if userId.count(',') == 0:

        userId = [userId]
    
    elif userId.count(',') > 0:

        userId = userId.split(',')

    currentCount = 0
    packet = []
    round = 0

    while True:
        for x in cookies:
            packet.append(x)
            round += 1

            if round >= int(amount):
                break

        if round >= int(amount):
            break

    while True:
        time.sleep(1)

        if len(packet) == 0 and len(threading_queue) == 0:
            break 

        if len(threading_queue) <= 1:

            for x in range(threads):
                
                thread_cookies = []

                for y in range(workers):
                    
                    if len(packet) != 0:
                        cookie = random.choice(packet)
                        packet.remove(cookie)
                        thread_cookies.append(cookie)


                for ii in thread_cookies:

                    threading_queue.append(ii)

                threading.Thread(target=report_botter_handle, args=(thread_cookies,userId,)).start()

    print(idle_color + f'> Task Finished, {success_color}Report botter..')
    input()


# Group Join Bot

def sendGroupJoin(cookie, groupIds, proxy):
    try:
        global currentCount
        
        for groupId in groupIds:

            timeStamp = time.time()


            with requests.session() as session:
                old_cookie = cookie
                old_proxy = proxy

                if config['cookies']['format'] != 0:

                    cookie = '_|' + cookie.split('_|')[1]
                
                session.cookies['.ROBLOSECURITY'] = cookie

                session.headers['user-agent'] = random.choice(agents)

                if proxyFormat != 0:

                    proxy_addr = proxy.split(':')

                    proxy_port = proxy_addr[1]
                    proxy_username = proxy_addr[2]
                    proxy_password = proxy_addr[3]
                    proxy_addr = proxy_addr[0]

                    session.proxies = {
                        'http':f'{proxyType}://' + proxy_username + ':' + proxy_password + '@' + proxy_addr + ':' + proxy_port,
                        'https':f'{proxyType}://' + proxy_username + ':' + proxy_password + '@' + proxy_addr + ':' + proxy_port
                    }

                elif proxyFormat == 0:

                    session.proxies = {
                        'http':f'{proxyType}://' + proxy,
                        'https':f'{proxyType}://' + proxy
                    }

                captcha = get_captcha_data(cookie, proxy, 'group', groupId)

                captchaBlob = captcha[1]
                captchaId = captcha[0]
    
                token, taskId = solveCaptcha(captchaBlob, '63E4117F-E727-42B4-6DAA-C8448E9B137F', f'https://www.roblox.com/groups/{groupId}')
                

                session.headers['x-csrf-token'] = session.post(
                    'https://friends.roblox.com/v1/users/1/request-friendship'
                ).headers['x-csrf-token']

                groupJoin = session.post(
                    f'https://groups.roblox.com/v1/groups/{groupId}/users',

                    data = {
                        'captchaId':captchaId,
                        'captchaProvider':'PROVIDER_ARKOSE_LABS',
                        'captchaToken':token
                    }
                )


                output = {
                    'taskTime':time.time() - timeStamp,
                    'proxy':proxy,
                    'target':groupId
                }


                if groupJoin.status_code == 200:
                    requests.post(
                        f'http://2captcha.com/res.php?key={two_captcha_key}&action=reporgood&id={taskId}'
                    )
                    print_queue.append(idle_color + f'> Joined Group:{success_color} {output}')
                
                elif groupJoin.status_code != 200:
                    requests.post(
                        f'http://2captcha.com/res.php?key={two_captcha_key}&action=reportbad&id={taskId}'
                    )
                    print_queue.append(idle_color + f'> Error:{failed_color} Captcha failed')

        currentCount += 1
        threading_queue.remove(old_cookie)

    except Exception as error:
        threading_queue.remove(old_cookie)
        print_queue.append(idle_color + f'> Error:{failed_color} {error}')


def join_group_handle(inputData, groupIds):
    rotate_proxies = 0
    for x in inputData:
        threading.Thread(target=sendGroupJoin, args=(x,groupIds,proxies[rotate_proxies],)).start()
        rotate_proxies += 1

    if rotate_proxies >= len(proxies):
        rotate_proxies = 0


def select_group_join_bot():
    global currentCount, threading_queue, print_queue

    print(idle_color + '> If you have multiple groupIds seperate each one with ","')
    print(idle_color + f'> Enter GroupId(s):')
    groups = input('-: ')

    if groups.count(',') == 0:

        groups = [groups]
    
    elif groups.count(',') > 0:

        groups = groups.split(',')

    currentCount = 0
    packet = []
    round = 0

    for x in cookies:
        packet.append(x)
        round += 1

    while True:
        time.sleep(1)

        if len(packet) == 0 and len(threading_queue) == 0:
            break 

        if len(threading_queue) <= 1:

            for x in range(threads):
                
                thread_cookies = []

                for y in range(workers):
                    
                    if len(packet) != 0:
                        cookie = random.choice(packet)
                        packet.remove(cookie)
                        thread_cookies.append(cookie)


                for ii in thread_cookies:

                    threading_queue.append(ii)

                threading.Thread(target=join_group_handle, args=(thread_cookies,groups,)).start()

    print(idle_color + f'> Task Finished, {success_color}Group Join bot..')
    input()


# Vote bot

def launch_account(cookie, gameId):

    with requests.session() as session:
        try:

            if config['cookies']['format'] != 0:

                cookie = '_|' + cookie.split('_|')[1]
            
            session.cookies['.ROBLOSECURITY'] = cookie

            session.headers['x-csrf-token'] = session.post(
                'https://friends.roblox.com/v1/users/1/request-friendship'
            ).headers['x-csrf-token']


            session.headers['referer'] = f'https://www.roblox.com/'
            session.headers['origin'] = 'https://www.roblox.com'
            session.headers['user-agent'] = random.choice(agents)

            authentication_ticket = session.post(
                'https://auth.roblox.com/v1/authentication-ticket/'
            ).headers['rbx-authentication-ticket']

            browserSig = random.randint(10000000,10000000000)

            os.startfile(f'roblox-player:1+launchmode:play+gameinfo:{authentication_ticket}+launchtime:{random.randint(10000,1000000)}+placelauncherurl:https%3A%2F%2Fassetgame.roblox.com%2Fgame%2FPlaceLauncher.ashx%3Frequest%3DRequestGame%26browserTrackerId%3D{browserSig}%26placeId%3D{gameId}%26isPlayTogetherGame%3Dfalse+browsertrackerid:{browserSig}+robloxLocale:en_us+gameLocale:en_us+channel:')

            time.sleep(14)

            return True
        
        except:

            return False


def sendLike(cookie, gameId, proxy, vote):
    try:

        with requests.session() as session:

            if config['cookies']['format'] != 0:

                cookie = '_|' + cookie.split('_|')[1]
            
            session.cookies['.ROBLOSECURITY'] = cookie

            session.headers['user-agent'] = random.choice(agents)

            session.headers['x-csrf-token'] = session.post(
                'https://friends.roblox.com/v1/users/1/request-friendship'
            ).headers['x-csrf-token']

            if proxyFormat != 0:

                proxy_addr = proxy.split(':')

                proxy_port = proxy_addr[1]
                proxy_username = proxy_addr[2]
                proxy_password = proxy_addr[3]
                proxy_addr = proxy_addr[0]

                session.proxies = {
                    'http':f'{proxyType}://' + proxy_username + ':' + proxy_password + '@' + proxy_addr + ':' + proxy_port,
                    'https':f'{proxyType}://' + proxy_username + ':' + proxy_password + '@' + proxy_addr + ':' + proxy_port
                }

            elif proxyFormat == 0:

                session.proxies = {
                    'http':f'{proxyType}://' + proxy,
                    'https':f'{proxyType}://' + proxy
                }

            
            session.headers['referer'] = f'https://www.roblox.com/games/{gameId}'
            session.headers['origin'] = 'https://www.roblox.com'

            
            likeGame = session.post(
                f'https://www.roblox.com/voting/vote?assetId={gameId}&vote=true'
            )

            if likeGame.json()['success'] == True:

                output = {
                    'success':True,
                    'proxy':proxy,
                    'vote':vote
                }

                print_queue.append(idle_color + f'> Liked game:{success_color} {output}')

            else:

                print_queue.append(idle_color + f'> Error:{failed_color} Failed to place vote')

    except Exception as error:
        print_queue.append(idle_color + f'> Error:{failed_color} {error}')


def select_vote_bot():
    global currentCount, threading_queue, print_queue
    print(failed_color +'::WARNING: Make sure your cookies meet the requirements for this feature')
    print(idle_color + '> Please provide the gameId you would like to "Vote bot" on')
    print(idle_color + f'> Enter GameId: ')
    gameId = input('-: ')

    print(idle_color + '\n> Please provide the amount of votes')
    print(idle_color + f'> Enter amount: ')
    amount = input('-: ')

    print(idle_color + '\n> Please select a vote method:\n(1): True, (2): False, (3): None')
    print(idle_color + f'> Selection: ')
    method = input('-: ')

    votes = [True, False, None]

    method = votes[int(method)-1]
 

    if len(cookies) < int(amount):

        amount = len(cookies)
    

    success_votes = 0
    loop = 0

    while True:

        if success_votes >= int(amount):
            break

        joined = launch_account(cookies[loop], gameId)
        
        if joined == True:
            liked = sendLike(cookies[loop], gameId, random.choice(proxies), method)

            if liked == True:
                 success_votes += 1

        loop += 1
            


# Main Menu #

def main():
    subprocess.getoutput('cls')


    cookies = open('cookies//cookies.txt', 'r').read().splitlines()
    proxies = open('proxies//proxies.txt', 'r').read().splitlines()

    features_color = colors[config['theme']['theme_colors']['features']]
    logo_color = colors[config['theme']['theme_colors']['logo']]


    features = [
        select_cookie_check, 
        select_proxy_check,
        select_description_checker,
        select_friends_checker,
        select_robux_checker,
        select_verified_checker,
        select_follow_bot,
        select_friend_bot,
        select_report_botter,
        select_group_join_bot,
        select_vote_bot
    ]

    print(logo_color + f'''
                       .------..------..------..------..------..------..------. 
                       |{features_color}S.--. {logo_color}||{features_color}K.--. {logo_color}||{features_color}Y.--. {logo_color}||{features_color}F.--. {logo_color}||{features_color}I.--. {logo_color}||{features_color}L.--. {logo_color}||{features_color}L.--.{logo_color} |
                       |{features_color} :/\: {logo_color}||{features_color} :/\: {logo_color}||{features_color} (\/) {logo_color}||{features_color} :(): {logo_color}||{features_color} (\/) {logo_color}||{features_color} :/\: {logo_color}||{features_color} :/\:{logo_color} |
                       |{features_color} :\/: {logo_color}||{features_color} :\/: {logo_color}||{features_color} :\/: {logo_color}||{features_color} ()() {logo_color}||{features_color} :\/: {logo_color}||{features_color} (__) {logo_color}||{features_color} (__){logo_color} |
                       |{features_color} '--'S{logo_color}||{features_color} '--'K{logo_color}||{features_color} '--'Y{logo_color}||{features_color} '--'F{logo_color}||{features_color} '--'I{logo_color}||{features_color} '--'L{logo_color}||{features_color} '--'L{logo_color}|
                       `------'`------'`------'`------'`------'`------'`------{logo_color}'

                                       {features_color}> Developer:{logo_color} sslprograms{features_color}
                                       > Cookies:{logo_color} {len(cookies)}{features_color}
                                       > Proxies:{logo_color} {len(proxies)}{features_color}

{logo_color} Skyfill is currently in its testing stages, more features will be presented in the future our tool has quality and speed that no other tool can beat skyfill is on top!
    ''' + features_color)

    print('======================================================================================================')


    print(features_color + '''
                  (1): Cookie Checker / (2): Proxy Checker / (3): Description Checker
                  (4): Friend Checker / (5): Robux Checker / (6): Verified Checker
                  (7): Follow Bot     / (8): Friend Bot    / (9): User Reporter
                  (10): Group Bot     / (11): Vote Bot     
    ''')

# / (12): Avatar Changer
#                   (13): Set Online    / (14): PM Bot       / (15): Friends Chat Bot
#                   (16): Model Sales   / (17): Favorite Bot / (18): Game Botter
#                   (19): Trade Spam    / (20): Trade Bot    / (21): Description Changer
#                   (22): Game Reporter / (23): Asset Buyer  / (24): Display Name Changer
#                   (25): Cookie Killer / (26): Reset Cookie / (27): Account Gen
#                   (29): Ally Bot      / (30): Unfollow Bot / (31): Visit Bot
#                   (32): Alt Gen       / (33): Asset Taker  / (34): Email Verifer

    print(idle_color + '\n======================================================================================================' + logo_color)
    try:
        playsound.playsound(f'config/other/startup.wav')
    except:
        pass
    selection = input('                 > ')


    features[int(selection)-1]()


    currentCount = 0
    subprocess.getoutput('mode con:cols=102 lines=31')
    subprocess.getoutput(f'title Skyfill v{vupdate}')
    main()


main()


