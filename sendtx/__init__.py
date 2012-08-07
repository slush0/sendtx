#!/usr/bin/python
'''
    @author slush <info@bitcoin.cz>
    @license sendtx is released as public domain.
'''

import sys
import multiprocessing
from twisted.internet import reactor, defer
from twisted.internet.protocol import ClientFactory
import StringIO
import binascii
import halfnode

success = False
debug = False

def log(msg):
    if not debug:
        return
    print msg

def send_failed():
    global success
    success = False
    log("FAILED")
    reactor.stop()
    
class P2PProtocol(halfnode.BitcoinP2PProtocol):
    def __init__(self, tx, send_or_check, on_connect):
        self.tx = tx # Transaction to broadcast or check
        self.txhash = None # Will be calculated in checking connection
        self.send_or_check = send_or_check # Is this broadcasting (True) or checking (False) instance?
        self.on_connect = on_connect # Deferred object waiting for establishing the connection
        
    def connectionMade(self):
        halfnode.BitcoinP2PProtocol.connectionMade(self)
        
        if self.on_connect:
            log("Checking connection ready")
            self.on_connect.callback(True)
            self.on_connect = None

        if self.send_or_check == True:
            # We're sending transaction
            self.broadcast_tx(self.tx)
            log("Transaction broadcasted to the network")
        else:
            # We're watching transaction
            tx = halfnode.msg_tx()
            tx.deserialize(StringIO.StringIO(binascii.unhexlify(self.tx)))
            tx.tx.calc_sha256()
            self.txhash = tx.tx.sha256
            log("Watching the network for %x" % self.txhash)
                
    def do_tx(self, message):
        '''Listen for transactions on bitcoin network. 
        Rebroadcasting our transaction by trusted bitcoin node indicates
        that transaction is valid and it has been accepted into memory pool.'''
        
        if self.send_or_check == False:
            message.tx.calc_sha256()
            log("Received tx %x" % message.tx.sha256)
            
            if message.tx.sha256 == self.txhash:
                global success
                success = True
                log("!!!! SUCCESFULLY SENT")
                
                # We stop the reactor so the program
                # flow will continue in _process()
                reactor.stop()
        
    def broadcast_tx(self, txdata):
        '''Broadcast new transaction (as a hex stream) to trusted node'''
        tx = halfnode.msg_tx()
        tx.deserialize(StringIO.StringIO(binascii.unhexlify(txdata)))
        self.send_message(tx)
        
class P2PFactory(ClientFactory):
    def __init__(self, tx, send_or_check, on_connect=None):
        self.tx = tx
        self.send_or_check = send_or_check
        self.on_connect = on_connect
        
    def buildProtocol(self, addr):
        return P2PProtocol(self.tx, self.send_or_check, self.on_connect)

def _process_send(_, host, tx):
    log("Initializing sending connection")
    reactor.connectTCP(host, 8333, P2PFactory(tx, True)) # Sending connection

def _process(host, tx, timeout):
    on_connect = defer.Deferred()
    on_connect.addCallback(_process_send, host, tx)
    
    log("Initializing checking connection")
    reactor.connectTCP(host, 8333, P2PFactory(tx, False, on_connect)) # Checking connection
    
    reactor.callLater(timeout, send_failed)
    reactor.run()
    
    global success
    if success == True:
        sys.exit(42)
        
def process_args():
    args = sys.argv[1:]
    if len(args) != 2:
        print "Usage: ./sendtx.py <bitcoin_node_hostname> <serialized_tx>"
        print "Result: Exit code '42' on success. Anything else means that some error occured (connection timeout, not accepted by memory pool, ...)"
        print "Example: ./sendtx.py localhost 01000000015210999277896c1a0c49c3071b6b2448d1d98c9880aefe50c0d00e79fa40ad64010000008b48304502207bb45481d4674837773878b184c7a59ebd3c87095322106355057411f89bd0ec02210084690f4b0ea00eeb8ad2c12ee603057433d04812317a65ea84aa605b5f643815014104e6a069738d8e8491a8abd3bed7d303c9b2dc3792173a18483653036fd74a5100fc6ee327b6a82b3df79005f101b88496988fa414af32df11fff3e96d53d26d03ffffffff0240420f00000000001976a914e1c9b052561cf0a1da9ee3175df7d5a2d7ff7dd488aca0252600000000001976a914f01ef5b20f08b93773c1152c5481a6e2d527096e88ac00000000"
        sys.exit()

    _process(args[0], args[1], 10)

def process(host, tx, timeout=10):
    p = multiprocessing.Process(target=_process, args=(host, tx, timeout))
    p.start()
    p.join()
    if p.exitcode != 42:
        raise Exception("Transaction broadcasting failed")

    t = halfnode.CTransaction()
    t.deserialize(StringIO.StringIO(binascii.unhexlify(tx)))
    t.calc_sha256()
    return "%x" % t.sha256

if __name__ == '__main__':
    process_args()
    #process('localhost2', '01000000015210999277896c1a0c49c3071b6b2448d1d98c9880aefe50c0d00e79fa40ad64010000008b48304502207bb45481d4674837773878b184c7a59ebd3c87095322106355057411f89bd0ec02210084690f4b0ea00eeb8ad2c12ee603057433d04812317a65ea84aa605b5f643815014104e6a069738d8e8491a8abd3bed7d303c9b2dc3792173a18483653036fd74a5100fc6ee327b6a82b3df79005f101b88496988fa414af32df11fff3e96d53d26d03ffffffff0240420f00000000001976a914e1c9b052561cf0a1da9ee3175df7d5a2d7ff7dd488aca0252600000000001976a914f01ef5b20f08b93773c1152c5481a6e2d527096e88ac00000000')