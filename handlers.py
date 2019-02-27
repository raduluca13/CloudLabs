import json
import mimetypes
import time
import uuid
from time import gmtime, strftime
import urllib.request
import urllib.parse
import requests
from urllib import parse
import config


def logger(**kwargs):
    pass


def split_headers(headers):
    h_dict = dict()
    # print("headers to split:", headers)
    for header in headers:
        splitted = header.split(":", 1)
        # print("splitted: ", splitted)
        h_dict[splitted[0]] = splitted[1].strip()
    # for header in headers
    return h_dict


def split_params(params):
    p_dict = dict()
    if params.count("&") > 0:
        params = params.split("&")
        for param in params:
            splitted = param.split("=")
            p_dict[splitted[0]] = splitted[1]
    else:
        splitted = params.split("=")
        p_dict[splitted[0]] = splitted[1]
    return p_dict


def handle_new_client(connection, address):
    found = 0
    with open('threads.txt') as threadsInfo:
        for line in threadsInfo:
            if connection == line.split("\t")[1]:
                found = 1
                break
    if found == 0:
        with open("threads.txt", "a") as threadsInfo:
            threadId = uuid.uuid4()
            threadsInfo.write('thread(newclient):{thread}\tconnection: {connection}\n'.format(thread=threadId, connection=connection))

    request = connection.recv(1024)  # ?size
    startTime = time.time()
    with open("logging.txt", "a") as log:
        log.write("request: {request}\nstartTime: {startTime}\n".format(request=request, startTime=startTime))
    req = request.decode().split("\r\n")
    print("full request: ", req)

    headers = req[1:-2]  # 2 blank lines at the end
    headers = split_headers(headers)
    # print("headers: ", headers)

    # req[0] = method + url + protocol
    if req[0] is not "":
        method, route, protocol = req[0].split(" ")
        if protocol == "HTTP/1.1":
            if method == "GET":
                payload = get(connection, route, headers)
                # print("payload: ", payload)
            elif method == "POST":
                payload = post(connection, route, headers, req[-1])
            elif method == "PUT":
                payload = put(connection, route, headers)
            elif method == "DELETE":
                payload = delete(connection, route, headers)
            else:
                payload = "unknown method"
            http_response = "{protocol} {status_code}\r\n\r\n{payload}".format(protocol=protocol,
                                                                               status_code=config.status_code,
                                                                               payload=payload)
            # print(http_response)
            http_response = http_response.encode()
            endTime = time.time()
            duration = endTime - startTime
            with open("logging.txt", "a") as log:
                log.write('response: {response}\nendTime: {endTime}\nlatency: {latency}\n\n'
                          .format(response=http_response, endTime=endTime, latency=duration))
            connection.sendall(http_response)
        else:
            connection.sendall("protocol connection not supported".encode())

    else:  # handle empty request - keep it alive
        connection.sendall("empty request".encode())
    connection.close()


def get(connection, route, headers):
    payload = ''
    # print("route in get", route)
    if route.startswith("/favicon.ico"):
        with open('favicon.ico', 'rb') as fav:
            payload = fav.read()
    elif route.startswith("/getStatus"):
        url = "https://api.random.org/json-rpc/2/invoke"
        data = {
            'jsonrpc': '2.0',
            'method': "getUsage",
            'params': {
                'apiKey': '3635cafe-f195-4206-8852-dd80ce4b4ce6'
            },
            'id': 13
        }

        data = json.dumps(data)  # make it string
        data = data.encode("utf-8")  # encode in bytes

        headers = {
            'User-Agent': headers["user_agent"],
            'Content-Type': 'application/json'
        }

        apiReq = urllib.request.Request(url, data, headers)
        payload = urllib.request.urlopen(apiReq).read().decode()
        # print(payload)
    elif route == "/getRandom":
        url = "https://api.random.org/json-rpc/2/invoke"
        data = {
            'jsonrpc': '2.0',
            'method': "generateIntegers",
            'params': {
                'apiKey': config.apiKey['randomorg'],
                'n': 1,
                "min": 1,
                "max": 10
            },
            'id': 13
        }

        data = json.dumps(data)  # make it string
        data = data.encode("utf-8")  # encode in bytes

        headers = {
            'User-Agent': headers['User-Agent'],
            'Content-Type': 'application/json'
        }

        timer = time.time()
        with open("metrics.txt", "a") as metrics:
            # it s ok with data ?
            metrics.write('serviceUrl: {service}\ndata: {data}\nstartTime: {startTime}\n\n'
                          .format(service=url, data=data, startTime=timer))

        apiReq = urllib.request.Request(url, data, headers)
        response = urllib.request.urlopen(apiReq).read()

        timer2 = time.time()
        latency = timer2 - timer
        with open("metrics.txt", "a") as metrics:
            # it s ok with data ?
            metrics.write('endTime: {endTime}\nresponse: {response}\nlatency: {latency}\n\n'
                          .format(endTime=timer2, response=response, latency=latency))
        loaded = json.loads(response.decode())

        result = loaded["result"]
        resultNumber = result["random"]["data"][0]
        payload = resultNumber
    elif route.startswith("/useService"):
        url = "https://api.random.org/json-rpc/2/invoke"
        data = {
            'jsonrpc': '2.0',
            'method': "generateIntegers",
            'params': {
                'apiKey': config.apiKey['randomorg'],
                'n': 1,
                "min": 1,
                "max": 10
            },
            'id': 13
        }

        data = json.dumps(data)  # make it string
        data = data.encode("utf-8")  # encode in bytes

        headers = {
            'User-Agent': headers['User-Agent'],
            'Content-Type': 'application/json'
        }

        timer = time.time()
        with open("metrics.txt", "a") as metrics:
            # it s ok with data ?
            metrics.write('serviceUrl: {service}\ndata: {data}\nstartTime: {startTime}\n\n'
                          .format(service=url, data=data, startTime=timer))

        apiReq = urllib.request.Request(url, data, headers)
        response = urllib.request.urlopen(apiReq).read()

        timer2 = time.time()
        latency = timer2 - timer
        with open("metrics.txt", "a") as metrics:
            # it s ok with data ?
            metrics.write('endTime: {endTime}\nresponse: {response}\nlatency: {latency}\n\n'
                          .format(endTime=timer2, response=response, latency=latency))
        loaded = json.loads(response.decode())

        result = loaded["result"]
        resultNumber = result["random"]["data"][0]
        # print("random ", resultNumber)

        url = "http://www.splashbase.co/api/v1/images/{id}"
        timer = time.time()
        with open("metrics.txt", "a") as metrics:
            # it s ok with data ?
            metrics.write('serviceUrl: {service}\ndata: {data}\nstartTime: {startTime}\n\n'
                          .format(service=url, data=b'', startTime=timer))

        content = urllib.request.urlopen(url.format(id=resultNumber)).read()

        timer2 = time.time()
        latency = timer2 - timer
        with open("metrics.txt", "a") as metrics:
            # it s ok with data ?
            metrics.write('endTime: {endTime}\nresponse: {response}\nlatency: {latency}\n\n'
                          .format(endTime=timer2, response=response, latency=latency))

        loaded = json.loads(content.decode())

        urlDl = loaded["url"]  # large_url too big. useless
        # print("url of downloaded resource: ",urlDl)
        local_filename, headers = urllib.request.urlretrieve(urlDl, "D:/Radu/facultate/cloud/random.jpg")
        # print(local_filename, headers)

        # send for checking
        url = "https://www.virustotal.com/vtapi/v2/file/scan"
        data = ''
        # with open("D:/Radu/facultate/cloud/random.jpg", 'rb') as f:
        #     data = f.read()
        params = {'apikey': config.apiKey['virustotal']}
        files = {'file': ('random.jpg', open('D:/Radu/facultate/cloud/random.jpg', 'rb'))}

        timer = time.time()
        with open("metrics.txt", "a") as metrics:
            # it s ok with data ?
            metrics.write('serviceUrl: {service}\ndata: {data}\nstartTime: {startTime}\n\n'
                          .format(service=url, data=b'', startTime=timer))

        response = requests.post('https://www.virustotal.com/vtapi/v2/file/scan', files=files, params=params)
        timer2 = time.time()
        latency = timer2 - timer
        with open("metrics.txt", "a") as metrics:
            # it s ok with data ?
            metrics.write('endTime: {endTime}\nresponse: {response}\nlatency: {latency}\n\n'
                          .format(endTime=timer2, response=response.json(), latency=latency))

        json_response = response.json()
        scan_id = json_response["scan_id"]
        res = json_response["resource"]
        payload = {
            "number": resultNumber,
            "src": urlDl,
            "resource": res,
            "scan_id": scan_id
        }
        payload = json.dumps(payload)
    elif route.startswith("/getImage"):
        payload = urllib.request.urlopen("http://www.splashbase.co/api/v1/images/random").read().decode()
    elif route.startswith("/metrics"):
        with open("metrics.txt", "r") as metrics:
            # print("reading ", metrics.read())
            payload = metrics.read()
    elif route == "/":
        with open('index.html') as index:
            payload = index.read()
    else:
        print("else", route, headers)
    return payload


def post(connection, route, headers, params=''):
    if route.startswith("/checkScanResult"):
        # retrieve scan report
        params = json.loads(params)
        url = 'https://www.virustotal.com/vtapi/v2/file/report'

        # scanID = '65d770f9d05ea6ff6f795914e8497cb2fd8057013e2d04d65edbad713d57fd17-1551221047'
        # sendableParams = {'apikey': config.apiKey['virustotal'], 'scan_id': scanID}

        sendableParams = {
            'apikey': config.apiKey['virustotal'],
            'resource': params["resource"],
            'scan_id': params['scan_id']
        }
        hheaders = {
            "Accept-Encoding": "gzip, deflate",
            # "User-Agent": "gzip,  My Python requests library example client or username"
            "User-Agent": headers["User-Agent"]
        }

        timer = time.time()
        with open("metrics.txt", "a") as metrics:
            # it s ok with data ?
            metrics.write('serviceUrl: {service}\ndata: {data}\nstartTime: {startTime}\n\n'
                          .format(service=url, data=sendableParams, startTime=timer))

        response = requests.get(url, params=sendableParams, headers=hheaders)

        timer2 = time.time()
        latency = timer2 - timer
        with open("metrics.txt", "a") as metrics:
            # it s ok with data ?
            metrics.write('endTime: {endTime}\nresponse: {response}\nlatency: {latency}\n\n'
                          .format(endTime=timer2, response=response.json(), latency=latency))
        timer = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        response = response.json()
        try:
            scans = response["scans"]
            scann = ''
            print("scans (response): ", scans)
            with open("responses.txt", "a") as res:
                for scan in scans:
                    scann = scan
                    res.write('{timer}\n{response}\n\n'.format(timer=timer, response=scans[scan]["detected"]))
                    break
            return scans[scann]["detected"]
        except:
            return "no file selected"
    if route.startswith("/getImage"):
        print(params)
        params = split_params(json.loads(params))
        url = "http://www.splashbase.co/api/v1/images/{id}"
        timer = time.time()
        with open("metrics.txt", "a") as metrics:
            # it s ok with data ?
            metrics.write('serviceUrl: {service}\ndata: {data}\nstartTime: {startTime}\n\n'
                          .format(service=url, data=b'', startTime=timer))

        content = urllib.request.urlopen(url.format(id=params["id"])).read()

        timer2 = time.time()
        latency = timer2 - timer
        with open("metrics.txt", "a") as metrics:
            # it s ok with data ?
            metrics.write('endTime: {endTime}\nresponse: {response}\nlatency: {latency}\n\n'
                          .format(endTime=timer2, response=content, latency=latency))

        loaded = json.loads(content.decode())
        return loaded["url"]
    else:
        return get(connection, '/index.html', headers)


def put(connection, route, headers, params=''):
    print(route, params)
    return 'put not yet supported'


def delete(connection, route, headers, params=''):
    print(route, params)
    return 'delete not yet supported'
