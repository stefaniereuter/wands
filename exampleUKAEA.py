from wands import RandomData, AdiosWands

params={
    "IPAddress": "127.0.0.1",
    "Port": "12306",
    "Timeout": "5",
    "TransportMode": "reliable", 
    "RendezvousReaderCount": "1",
}

ads = AdiosWands(link="DeclaredIO2", parameters=params)
receiveddata = ads.receive(eng_name="IO1",variable_name="req_list")

print(receiveddata)