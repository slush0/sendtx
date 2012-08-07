sendtx
======

Python module for sending bitcoin transaction directly to the bitcoin network

What: This module broadcast given bitcoin transaction into Bitcoin network
using just P2P connection to some trusted Bitcoin node.
    
Why: No bitcoind patches needed anymore..
    
How: Library creates two connections to the trusted node: One listen for new transactions
on the network, second sends serialized transaction to the network. Trusted node
make internal checks and if the transaction is valid, it accepts the transaction
into it's memory pool and rebroadcast it to connected peers...
...so when our second (checking) connection sniff our txhash on the bitcoin network,
we have a confirmation that the transaction has been succesfully accepted
by the network.
    
This library is built on top of ArtForz's half node with some modifications
for Twisted framework. For this reason I'm using the hack with subprocess module, 
so calling application don't need to care about Twisted stuff.
    
Commandline example: ./sendtx.py localhost 01000000015210999277896...0000000
Script returns exit code '42' on success.

Python script example:
#!/usr/bin/python    
import sendtx
try:
    sendtx.process('localhost', '01000000015210999277896...0000000')
except:
    print "Broadcast failed"
