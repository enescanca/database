# import module
import requests
from requests.auth import HTTPBasicAuth
import json

#Dongu
req = True
while req:
    #or DefaultValue
    username = input('Kullanici Adi [Administrator] : ') or 'Administrator'
    password = input('Parola: [password] : ') or 'password'
    server = input('Server: [172.17.0.2] : ') or '172.17.0.2'

    choice = input("\n0 - Manuel Giris.\n1 - Retrieves cluster information.\n2 - Retrieves parameter settings for the Index service.\n3 - Retrieves all bucket and bucket operations information from a cluster.\n4 - Daha fazlasi icin\n\n")
    choice = int(choice)
    if choice == 0:
        URI_path = input('URI Path:[pools] : ') or 'pools'
    elif choice == 1:
        URI_path = 'pools'
    elif choice == 2:
        URI_path = 'settings/indexes'
    elif choice == 3:
        URI_path = 'pools/default/buckets'
    elif choice == 4:
        print("https://docs.couchbase.com/server/current/rest-api/rest-endpoints-all.html#http-method-and-uri-list")
        quit()
    else:
        print("Yanlıs Tercih.")




    # İstek
    response = requests.get('http://' + server + ':8091/' + URI_path,
                            # authentication, user+pass
                            auth=HTTPBasicAuth(username, password))

    # okunulabilir json cıktı
    pretty_json = json.loads(response.text)
    print(json.dumps(pretty_json, indent=2))

    #Cıkıs
    if req == True:
        choice = input('Enter or Press Q to Quit : ')
        if choice == 'q':
            break
