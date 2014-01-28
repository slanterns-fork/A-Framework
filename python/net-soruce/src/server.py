#! /usr/bin/env python
# Copyright (C) 2008 Du XiaoGang 
# Copyright (C) 2012 LeZiZi Studio

import random, re, socket, Queue, time, select, errno, getpass 
from threading import Thread

import xmpp

import common
from stunclient import *
from parseconf import *



# global messages list
messages = []

# global varibles
quitNow = False

def xmppMessageCB(cnx, msg):
    u = msg.getFrom()
    m = msg.getBody()
    #print u, m
    if u and m:
        messages.append((str(u).strip(), str(m).strip()))
        #messages.append((unicode(u), unicode(m)))

def xmppListen(gtalkServerAddr, user, passwd,domain):
    cnx = xmpp.Client(domain, debug=[])
    conn = cnx.connect(server=gtalkServerAddr)
    if not conn:
        print "Unable to connect to server."
    auth =cnx.auth(user, passwd, resource=domain,sasl=0)
    if not auth:
        print "Unable to authorize - check login/password."
    cnx.sendInitPresence()
    cnx.RegisterHandler('message', xmppMessageCB)
    return cnx

def randStr():
    s = ''
    for i in range(common.SESSION_ID_LENGTH):
        s += random.choice('abcdefghijklmnopqrstuvwxyz')
    return s

class WorkerError(Exception):
    pass

class EstablishError(WorkerError):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return '<Establish Error: %s>' % self.reason

class TransferError(WorkerError):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return '<Transfer Error: %s>' % self.reason
    
class UIThread(Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        while True :
            try:
                testqueue.put(raw_input("_"))
            except Exception,e:
                print (e)
            
class WorkerThread(Thread):
    '''worker thread'''
    # srcUser without '/'
    def __init__(self, toAddr, i, myNetType, iQueue, oQueue, sessKey, \
                 srcNetType, srcAddr, srcUser, stunServerAddr):
        Thread.__init__(self)
        self.toAddr = toAddr
        self.i = i
        self.myNetType = myNetType 
        self.iQueue = iQueue
        self.oQueue = oQueue
        self.sessKey = sessKey 
        self.srcNetType = srcNetType 
        self.srcAddr = srcAddr
        self.srcUser = srcUser
        self.stunServerAddr = stunServerAddr

    def run(self):
        # prepare
        try:
            self.prepare()
        except Exception, e:
            self.cannotEstablish('Server internal error')
            print 'Catch exception when handling new request from %s at %s:' \
                  % (self.srcUser, self.srcAddr), e
            return
        # establish
        try:
            self.establish()
        except Exception, e:
            print 'Catch exception when trying to establish a new connection with %s at %s:' \
                  % (self.srcUser, self.srcAddr), e
            return
        print 'Connection is established with %s at %s.' % (self.srcUser, self.srcAddr)
        # transfer
        try:
            self.transfer()
        except Exception, e:
            print 'Catch exception when transfer data with %s at %s:' \
                  % (self.srcUser, self.srcAddr), e
            return
        print 'Disconnected with %s at %s.' % (self.srcUser, self.srcAddr)

    def prepare(self):
        # prepare for establish new connection
        self.toSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        self.fromSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        # MUST settimeout before call getMappedAddr
        self.fromSock.settimeout(1)
        sc = STUNClient()
        (self.myIP, self.myPort) = sc.getMappedAddr(self.fromSock, self.stunServerAddr)

    def establish(self):
        # have server and client got the same mapped ip?
        if self.myIP == self.srcAddr[0]:
            self.cannotEstablish('Two peers are in the same LAN')
            raise EstablishError('Two peers are in the same LAN')
        # opened or fullcone nat?
        elif self.myNetType == NET_TYPE_OPENED \
             or self.myNetType == NET_TYPE_FULLCONE_NAT:
            # tell client to connect
            self.establishIA((self.myIP, self.myPort), self.fromSock)
        elif self.srcNetType == NET_TYPE_OPENED \
             or self.srcNetType == NET_TYPE_FULLCONE_NAT:
            self.establishIB(self.fromSock)
        # restrict?
        elif self.myNetType == NET_TYPE_REST_FIREWALL \
             or self.myNetType == NET_TYPE_REST_NAT:
            # tell client to connect
            self.establishIIA((self.myIP, self.myPort), self.fromSock)
        elif self.srcNetType == NET_TYPE_REST_FIREWALL \
             or self.srcNetType == NET_TYPE_REST_NAT:
            self.establishIIB((self.myIP, self.myPort), self.fromSock)
        # both port restrict?
        elif (self.myNetType == NET_TYPE_PORTREST_FIREWALL \
              or self.myNetType == NET_TYPE_PORTREST_NAT) \
             and (self.srcNetType == NET_TYPE_PORTREST_FIREWALL \
                  or self.srcNetType == NET_TYPE_PORTREST_NAT):
            self.establishIII((self.myIP, self.myPort), self.fromSock)
        # one port restrict and one symmetric with localization
        elif (self.myNetType == NET_TYPE_PORTREST_FIREWALL \
              or self.myNetType == NET_TYPE_PORTREST_NAT) \
             and self.srcNetType == NET_TYPE_SYM_NAT_LOCAL:
            self.establishIVA((self.myIP, self.myPort), self.fromSock)
        elif (self.srcNetType == NET_TYPE_PORTREST_FIREWALL \
              or self.srcNetType == NET_TYPE_PORTREST_NAT) \
             and self.myNetType == NET_TYPE_SYM_NAT_LOCAL:
            self.fromSock = self.establishIVB((self.myIP, self.myPort), self.fromSock)
        # one port restrict and one symmetric
        elif (self.myNetType == NET_TYPE_PORTREST_FIREWALL \
              or self.myNetType == NET_TYPE_PORTREST_NAT) \
             and self.srcNetType == NET_TYPE_SYM_NAT:
            self.establishVA((self.myIP, self.myPort), self.fromSock)
        elif (self.srcNetType == NET_TYPE_PORTREST_FIREWALL \
              or self.srcNetType == NET_TYPE_PORTREST_NAT) \
             and self.myNetType == NET_TYPE_SYM_NAT:
            self.establishVB((self.myIP, self.myPort), self.fromSock)
        else:
            self.cannotEstablish('Peer\'s NAT type dismatched.')
            raise EstablishError('Peer\'s NAT type dismatched.')

    def transfer(self):
        # non-blocking IO
        self.fromSock.setblocking(False)
        self.toSock.setblocking(False)
        lastCheck = time.time()
        # transfer
        while True:
            # check to/from socket
            try:
                if not testqueue.empty():
                    self.fromSock.sendto(testqueue.get(), self.srcAddr)
                    print("*")
            except Exception, e:
                print(e)
                
            try:
                (rs,ws,es) = select.select([self.fromSock],[],[])
                if self.fromSock in rs:
                    while True:
                        (d, _) = self.fromSock.recvfrom(2048)
                        if (d == ''):
                            # preserve connection
                            break
                        else:
                            print(d)
            except socket.error, e:
                if e[0] != errno.EAGAIN and e[0] != 10035:
                    raise e
                # EAGAIN
            except Exception, e:
                print(e)
            
            # check iQueue
            t = time.time()
            if t - lastCheck >= 1:
                lastCheck = t
                # iQueue, mainly for management
                # preserve connection
                self.fromSock.sendto('', self.srcAddr)
            # quit?
            if quitNow:
                break

    # m is the actual message will be sent
    def sendXmppMessage(self, m):
        self.oQueue.put(m)

    def waitXmppMessage(self, timeout=None):
        if not timeout:
            timeout = common.TIMEOUT
        try:
            return self.iQueue.get(True, timeout)
        except Queue.Empty:
            return None

    def cannotEstablish(self, reason):
        self.sendXmppMessage('Cannot;%s;%s' % (reason, self.sessKey))

    def establishIA(self, addr, sock):
        #print 'establishIA()'
        self.sendXmppMessage('Do;IA;%s:%d;%s' % (addr[0], addr[1], self.sessKey))
        # wait for udp packet
        sock.settimeout(1)
        ct = time.time()
        while time.time() - ct < common.TIMEOUT:
            try:
                (data, fro) = sock.recvfrom(2048)
            except socket.timeout:
                continue
            # got some data
            if data == 'Hi;%s' % self.sessKey:
                sock.setblocking(True)
                sock.sendto('Welcome;%s' % self.sessKey, fro)
                self.srcAddr = fro
                return
        else:
            # timeout
            raise EstablishError('Timeout')

    def establishIB(self, sock):
        #print 'establishIB()'
        # tell client to wait for udp request
        self.sendXmppMessage('Do;IB;%s' % self.sessKey)
        # try to send udp packet
        sock.setblocking(True)
        sock.sendto('Hi;%s' % self.sessKey, self.srcAddr)
        sock.settimeout(1)
        ct = time.time()
        while time.time() - ct < common.TIMEOUT:
            try:
                (data, fro) = sock.recvfrom(2048)
            except socket.timeout:
                continue
            # got some data
            if fro == self.srcAddr and data == 'Welcome;%s' % self.sessKey:
                return
        else:
            # timeout
            raise EstablishError('Timeout')

    def establishIIA(self, addr, sock):
        #print 'establishIIA()'
        # punch
        sock.setblocking(True)
        sock.sendto('Punch', self.srcAddr)
        # tell client to connect
        self.sendXmppMessage('Do;IIA;%s:%d;%s' % (addr[0], addr[1], self.sessKey))
        # wait for udp packet
        sock.settimeout(1)
        ct = time.time()
        while time.time() - ct < common.TIMEOUT:
            try:
                (data, fro) = sock.recvfrom(2048)
            except socket.timeout:
                continue
            # got some data
            if data == 'Hi;%s' % self.sessKey:
                sock.setblocking(True)
                sock.sendto('Welcome;%s' % self.sessKey, fro)
                self.srcAddr = fro
                return
        else:
            # timeout
            raise EstablishError('Timeout')

    def establishIIB(self, addr, sock):
        #print 'establishIIB()'
        # tell client to punch and wait for udp request
        self.sendXmppMessage('Do;IIB;%s:%d;%s' % (addr[0], addr[1], self.sessKey))
        # wait for Ack
        ct = time.time()
        while time.time() - ct < common.TIMEOUT:
            m = self.waitXmppMessage()
            if not m:
                continue
            # got message
            if m == 'Ack;IIB;%s' % self.sessKey:
                break
        else:
            # timeout
            raise EstablishError('Timeout')
        # try to send udp packet
        sock.setblocking(True)
        sock.sendto('Hi;%s' % self.sessKey, self.srcAddr)
        sock.settimeout(1)
        ct = time.time()
        while time.time() - ct < common.TIMEOUT:
            try:
                (data, fro) = sock.recvfrom(2048)
            except socket.timeout:
                continue
            # got some data
            if fro == self.srcAddr and data == 'Welcome;%s' % self.sessKey:
                return
        else:
            # timeout
            raise EstablishError('Timeout')

    def establishIII(self, addr, sock):
        #print 'establishIII()'
        # punch
        sock.setblocking(True)
        sock.sendto('Punch', self.srcAddr)
        # tell client to do punch
        self.sendXmppMessage('Do;III;%s:%d;%s' % (addr[0], addr[1], self.sessKey))
        # wait for Ack
        ct = time.time()
        while time.time() - ct < common.TIMEOUT:
            m = self.waitXmppMessage()
            if not m:
                continue
            # got message
            if m == 'Ack;III;%s' % self.sessKey:
                break
        else:
            # timeout
            raise EstablishError('Timeout')
        # try to send udp packet
        sock.setblocking(True)
        sock.sendto('Hi;%s' % self.sessKey, self.srcAddr)
        # wait for Welcome
        sock.settimeout(1)
        ct = time.time()
        while time.time() - ct < common.TIMEOUT:
            try:
                (data, fro) = sock.recvfrom(2048)
            except socket.timeout:
                continue
            # got some data
            if fro == self.srcAddr and data == 'Welcome;%s' % self.sessKey:
                return
        else:
            # timeout
            raise EstablishError('Timeout')

    def establishIVA(self, addr, sock):
        #print 'establishIVA()'
        # tell client do IVA
        self.sendXmppMessage('Do;IVA;%s:%d;%s' % (addr[0], addr[1], self.sessKey))
        # wait for Ack
        ct = time.time()
        while time.time() - ct < common.TIMEOUT:
            m = self.waitXmppMessage()
            if not m:
                continue
            # got message
            if re.match(r'^Ack;IVA;\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5};%s$' \
                        % self.sessKey, m):
                break
        else:
            # timeout
            raise EstablishError('Timeout')
        # parse Ack to get IP:PORT
        ip = m.split(';')[2].split(':')[0]
        try:
            socket.inet_aton(ip)
        except socket.error:
            # invalid ip
            raise EstablishError('Invalid client message')
        port = int(m.split(';')[2].split(':')[1])
        # try to send udp packet to a range
        bp = port - common.LOCAL_RANGE
        if bp < 1:
            bp = 1
        ep = port + common.LOCAL_RANGE
        if ep > 65536:
            ep = 65536
        sock.setblocking(True)
        for p in range(bp, ep):
            sock.sendto('Hi;%s' % self.sessKey, (ip, p))
        # wait for Welcome
        sock.settimeout(1)
        ct = time.time()
        while time.time() - ct < common.TIMEOUT:
            try:
                (data, fro) = sock.recvfrom(2048)
            except socket.timeout:
                continue
            # got some data
            if data == 'Welcome;%s' % self.sessKey:
                self.srcAddr = fro
                return
        else:
            # timeout
            raise EstablishError('Timeout')

    def establishIVB(self, addr, sock):
        #print 'establishIVB()'
        # new socket
        newSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        # punch
        newSock.setblocking(True)
        newSock.sendto('Punch', self.srcAddr)
        # get new socket's mapped addr
        newSock.settimeout(1)
        sc = STUNClient()
        (mappedIP, mappedPort) = sc.getMappedAddr(newSock, self.stunServerAddr)
        # tell client the new addr (xmpp)
        self.sendXmppMessage('Do;IVB;%s:%d;%s' % (mappedIP, mappedPort, self.sessKey))
        # wait for client's 'Hi' (udp)
        newSock.settimeout(1)
        ct = time.time()
        while time.time() - ct < common.TIMEOUT:
            try:
                (data, fro) = newSock.recvfrom(2048)
            except socket.timeout:
                continue
            # got some data
            if fro == self.srcAddr and data == 'Hi;%s' % self.sessKey:
                # send client Welcome (udp)
                newSock.setblocking(True)
                newSock.sendto('Welcome;%s' % self.sessKey, fro)
                # !!! return newSock
                return newSock
        else:
            # timeout
            raise EstablishError('Timeout')

    def establishVA(self, addr, sock):
        #print 'establishVA()'
        # tell client do VA
        self.sendXmppMessage('Do;VA;%s:%d;%s' % (addr[0], addr[1], self.sessKey))
        # wait for client's Ack
        ct = time.time()
        while time.time() - ct < common.TIMEOUT:
            m = self.waitXmppMessage()
            if not m:
                continue
            # got message
            if re.match(r'^Ack;VA;%s$' % self.sessKey, m):
                break
        else:
            # timeout
            raise EstablishError('Timeout')
        # scan all ports of the server
        portBegin = 1
        while portBegin < 65536:
            sock.setblocking(True)
            # try to connect server's port range
            for p in range(portBegin, portBegin + common.SYM_SCAN_RANGE):
                if p < 65536:
                    # send client hi (udp)
                    port = (p + self.srcAddr[1] - common.SYM_SCAN_PRE_OFFSET) % 65536
                    sock.sendto('Hi;%s' % self.sessKey, (self.srcAddr[0], port))
            portBegin = p + 1
            # tell server we've sent Hi
            self.sendXmppMessage('Done;VASent;%s' % self.sessKey)
            # wait for any message, both udp and xmpp.
            sock.setblocking(False)
            ct = time.time()
            while time.time() - ct < common.TIMEOUT:
                m = self.waitXmppMessage(1)
                # did we receive client's 'Welcome'(udp)?
                try:
                    (data, fro) = sock.recvfrom(2048)
                    # got some data
                    if 'Welcome;%s' % self.sessKey:
                        # connection established
                        self.srcAddr = fro
                        return
                except socket.error, e:
                    if e[0] != errno.EAGAIN and e[0] != 10035:
                        raise e
                    # EAGAIN, ignore
                # process messages
                if not m:
                    continue
                elif m == 'Ack;VA;%s' % self.sessKey:
                    # next range
                    break
            else:
                raise EstablishError('Timeout')
        else:
            raise EstablishError('Failed to try')

    def establishVB(self, addr, sock):
        #print 'establishVB()'
        while True:
            # punch
            sock.setblocking(True)
            sock.sendto('Punch', self.srcAddr)
            # tell client do VB
            self.sendXmppMessage('Do;VB;%s:%d;%s' % (addr[0], addr[1], self.sessKey))
            # wait for client's Ack
            ct = time.time()
            while time.time() - ct < common.TIMEOUT:
                m = self.waitXmppMessage()
                if not m:
                    continue
                # got message
                if re.match(r'^Ack;VB;%s$' % self.sessKey, m):
                    break
            else:
                # timeout
                raise EstablishError('Timeout')
            # have we received client's hello?
            sock.setblocking(False)
            while True:
                try:
                    (data, fro) = sock.recvfrom(2048)
                except socket.error, e:
                    if e[0] != errno.EAGAIN and e[0] != 10035:
                        raise e
                    # EAGAIN
                    break
                # got some data
                if fro == self.srcAddr and data == 'Hi;%s' % self.sessKey:
                    sock.setblocking(True)
                    sock.sendto('Welcome;%s' % self.sessKey, fro)
                    return
                
def processInputMessages(sc, ms, ss, stunServerAddr):
    while True:
        try:
            # FIFO
            (u, c) = ms.pop(0)
        except IndexError:
            break
        # check client user
        #print 'user:', u
        if u.partition('/')[0] not in sc.getAllowedUser():
            continue
        # process content 
        #print 'Input xmpp message:', c
        if re.match(r'^Hello;\d+;\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}$', c):
            # client hello
            iq = Queue.Queue()
            oq = Queue.Queue()
            # get a new session key
            while True:
                k = randStr()
                if k not in ss.keys():
                    break
            # parse client hello
            t = int(c.split(';')[1])
            ip = c.split(';')[2].split(':')[0]
            try:
                socket.inet_aton(ip)
            except socket.error:
                # invalid ip
                continue
            p = int(c.split(';')[2].split(':')[1])
            wt = WorkerThread(sc.getToAddr(), sc.getLoginUser(), sc.getNetType(), \
                              iq, oq, k, t, (ip, p), u.partition('/')[0], stunServerAddr)
            # u include '/'
            ss[k] = (u, iq, oq)
            wt.start()
        elif re.match(r'^Ack;[A-Z]{2,3};[a-z]{%d}$' % common.SESSION_ID_LENGTH, c): 
            # Ack
            k = c.split(';')[2]
            if k in ss.keys():
                (mu, iq, _) = ss[k]
                if mu == u:
                    iq.put(c)
        elif re.match(r'^Ack;IVA;\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5};[a-z]{%d}$' \
                      % common.SESSION_ID_LENGTH, c):
            # Ack;IVA
            k = c.split(';')[3]
            if k in ss.keys():
                (mu, iq, _) = ss[k]
                if mu == u:
                    iq.put(c)

def processOutputMessage(cnx, ss):
    # for each session
    for k in ss.keys():
        (u, _, oq) = ss[k]
        # for each message
        while True:
            try:
                m = oq.get_nowait()
            except Queue.Empty:
                break
            # send
            #print 'Output xmpp message:', m
            cnx.send(xmpp.Message(u, m))

def main():
    global quitNow

    sessions = {}

    # open server configuration file
    serverConf = ServerConf('./server.conf')
    # get network type
    netType = serverConf.getNetType()
    if netType == NET_TYPE_UDP_BLOCKED:
        # blocked
        print 'UDP is blocked by the firewall!'
        return
    # get stun server's addr
    stunServerAddr = serverConf.getSTUNServer()
    # get gtalk server's addr
    gtalkServerAddr = serverConf.getGTalkServer()
    # get user info of xmpp(gtalk) 
    user = serverConf.getLoginUser()
    passwd = getpass.getpass('Password for %s: ' % user)
    # get user domain
    domain = serverConf.getValue('domain')

    # USER INTEFACE
    global testqueue
    testqueue = Queue.Queue()
    uitd = UIThread()
    uitd.start()
    
    # wait for messages from xmpp server
    while True:
        try:
            # the outer 'while' is for connection lost.
            cnx = xmppListen(gtalkServerAddr, user, passwd,domain)
            print 'XMPP starts to listen.'
            while True:
                cnx.sendPresence()
                # keep connection alive
                if not cnx.Process(1):
                    print 'XMPP lost connection.'
                    break
                # process messages
                processInputMessages(serverConf, messages, sessions, stunServerAddr)
                processOutputMessage(cnx, sessions)
        except KeyboardInterrupt:
            quitNow = True
            break
        except Exception, e:
            print 'Catch exception:', e

if __name__ == '__main__':
    main()
