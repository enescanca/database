# System Infrastructure Bootcamp - Database

## 1.Case

### Ön Gerekilikler

|Ön Gereklilik | Versiyon|
|-----------------|----------------------|
| Docker Compose      | 1.25.0 |      
| Python     | v3.0+ |      
| Docker      | 20.10.2  |      

### Containers

| Container  Name | Network Configuration| Image               |
|-----------------|----------------------|---------------------|
| couchbase1            | IP: 172.17.0.2       | couchbase/server    |
| couchbase2          | IP: 172.17.0.3       | couchbase/server    |
| couchbase3          | IP: 172.17.0.4       | couchbase/server    |

#### Container'ların ayağa kaldırılması

Öngereklilikler karşılandıktan sonra `docker-compose.yml` konfigürasyon dosyasının buludnduğu dizinde önceden belirlediğimiz container'ları `docker-compose up` komutu ile ayağı kaldırıyoruz.

- Ayağa kaldırılan container'ların kontrolü sağlanır.
```sh
❯ docker ps

CONTAINER ID   IMAGE              COMMAND                  CREATED       STATUS       PORTS                                                                                                              NAMES
2b3af47cdf4c   couchbase/server   "/entrypoint.sh couc…"   2 hours ago   Up 2 hours   8094-8096/tcp, 0.0.0.0:8091-8093->8091-8093/tcp, 11207/tcp, 11211/tcp, 0.0.0.0:11210->11210/tcp, 18091-18096/tcp   database_couchbase1
980345dc312a   couchbase/server   "/entrypoint.sh couc…"   2 hours ago   Up 2 hours   8091-8096/tcp, 11207/tcp, 11210-11211/tcp, 18091-18096/tcp                                                         database_couchbase2
21b846d1859c   couchbase/server   "/entrypoint.sh couc…"   2 hours ago   Up 2 hours   8091-8096/tcp, 11207/tcp, 11210-11211/tcp, 18091-18096/tcp                                                         database_couchbase3

```
- Network bilgisi edinilir.

```sh
❯ docker inspect -f '{{.Name}} - {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(docker ps -aq)

/database_couchbase1 - 172.17.0.2
/database_couchbase2 - 172.17.0.3
/database_couchbase2 - 172.17.0.4

```
#### Couchbase Cluster Yapısının oluşturulması

 Manager olarak kullanacağımız makina belirlenerek shell'ine erişilir.

`❯ docker exec -it database_couchbase1 bash`

İlk cluster da gerekli parametreler konfigüre edilerek komut çalıştırılır.


```sh
❯ couchbase-cli cluster-init -c 172.17.0.2 --cluster-username Administrator \
 --cluster-password password --services data,index,query,fts,analytics \
 --cluster-ramsize 256 --cluster-index-ramsize 256 \
 --cluster-eventing-ramsize 256 --cluster-fts-ramsize 256 \
 --cluster-analytics-ramsize 1024 --cluster-fts-ramsize 256 \
 --index-storage-setting default

 #SUCCESS: Cluster initialized

```
> Bir sonraki adıma geçmeden yukarıdaki işlem her couchbase server için uygulanmalıdır.

```sh
❯ couchbase-cli server-add -c 172.17.0.2:8091 --username Administrator \
--password password --server-add http://172.17.0.3:8091 \
--server-add-username Administrator --server-add-password password

#SUCCESS: Server added
```
> 172.17.0.4 için de uygulanmalıdır.

#### Couchbase Cluster Yapısının Dengelenmesi(Rebalance)

>Yeniden dengeleme, verileri ve dizinleri mevcut düğümler arasında yeniden dağıtma işlemidir.

```sh
❯ couchbase-cli rebalance -c 172.17.0.2:8091 --username Administrator \
 --password password


# Rebalancing
 Bucket: 00/00 ()                                                                                      0 docs remaining
 [============================================================================================================] 100.00%
 SUCCESS: Rebalance complete
```
Yukarıdaki çıktıda görüldüğü üzere hiçbit "Bucket"'a sahip değiliz.
>El ile bir Bucket oluşturulup içine veri eklenebilir fakat couchbase tarafından sağlanan sample-bucket'ı kullanmayı tercih edeceğim.

``` sh
❯ /opt/couchbase/bin/cbdocloader -c 172.17.0.2:8091 \
-u Administrator -p password -b travel-sample -m 100 \
-d /opt/couchbase/samples/travel-sample.zip

OR

❯ curl -X POST -u Administrator:password \
http://172.17.0.2:8091/sampleBuckets/install \
-d '["travel-sample"]'
```
> cbdocloader ile kaynak yetersizliğinden kaynaklı hata alınırsa curl ile bucket eklenmesi tercih edilebilir.

Tekrar yapılan rebalance işleminde görüldüğü üzere Bucket sayısı 1'e yükselmiştir.
```
#Bucket: 01/01 (travel-sample)                                                                         * docs remaining
[============================================================================================================] 100.00%
SUCCESS: Rebalance complete
```

N1QL Sorgusu İle Bucket Kontrolünün Sağlanması

``` json
❯cbq> SELECT callsign FROM `travel-sample` LIMIT 5;

#{
    "requestID": "a67f3819-a791-4eb2-8616-b83c300ea2d7",
    "signature": {
        "callsign": "json"
    },
    "results": [
    {
        "callsign": "MILE-AIR"
    },
    {
        "callsign": "TXW"
    },
    {
        "callsign": "atifly"
    },
    {
        "callsign": null
    },
    {
        "callsign": "LOCAIR"
    }
    ],
    "status": "success",
    "metrics": {
        "elapsedTime": "2.642504ms",
        "executionTime": "2.544358ms",
        "resultCount": 5,
        "resultSize": 175
    }
}
```
## 2.Case

Programın çekirdeği Coucbase REST API'sini kullanarak bulunan GET veya POST isteklerininJSON çıktısını uygun bir şekilde parse ederek "Human Readable" formatta çıktısını sağlamasından oluşmaktadır.
> Program üzerinden özel olarak sorgu yapabilir veya üzerinde hazır bulunan isteklerden birini tercih edebilirsiniz.

``` python
    # İstek
    response = requests.get('http://' + server + URI_path,
                            # authentication, user+pass
                            auth=HTTPBasicAuth(username, password))

    # okunulabilir json cıktı
    pretty_json = json.loads(response.text)
    print(json.dumps(pretty_json, indent=2))
```
#### Kaynaklar
- https://hub.docker.com/_/couchbase
- https://docs.couchbase.com/server/current/rest-api/rest-endpoints-all.html
- https://docs.couchbase.com/server/current/cli/cbcli/couchbase-cli.html
