
import threading
import zmq
import sys
import numpy as np
from collections import deque
from struct import *

class Backend(threading.Thread):

    def __init__(self, addr="127.0.0.1", port=5555):

        print(addr, port)
        self.addr = addr
        self.port = int(port)
        self.ml=50

        threading.Thread.__init__(self)
        self.startConnection()
        self.Z =  {}


    def receiveTopics(self, string, verbose):
        """
        Receive topic information from sender
        """

        # name (identifier of topic)
        sizeString  = int(string[1])
        name        = string[2:sizeString+2].decode("utf-8")
        print(sizeString)
        print(name)

        sizeIndex   = int(string[sizeString+2])
        index       = string[sizeString+3:sizeString+sizeIndex+3].decode("utf-8") if sizeIndex else ""

        sizePlot    = int(string[sizeString+sizeIndex+3])
        plotStyle   = string[sizeString+sizeIndex+4:sizeString+sizeIndex+sizePlot+4].decode("utf-8")

        pos = sizeString + sizeIndex + sizePlot + 4
        amountParams= int(string[pos])
        sizeType    = int(string[pos+1])
        dataType    = string[pos+2:pos+3].decode("utf-8")
        bufferSize  = unpack('Q', string[pos+3:pos+3+8])[0]

        pos = pos+3+8
  
        sizeTuple   = sizeType * amountParams
        amountTuples= int((len(string) - pos) / sizeTuple);

        if not self.Z.get(name): self.Z[name] = {index: [plotStyle, np.array([])]}
        elif not len(self.Z[name].get(index, [])) : self.Z[name][index] = [plotStyle, np.array([])]

        if verbose: print("name='" +  name +  "', index='" + index 
                    + "', #Params=",  amountParams, ", #Tuples=", amountTuples,
                    "Type='" +  dataType + "'.size=", sizeType)
        for i in range(amountTuples):
            pi = pos + i * sizeTuple

            au =  string[pi + 0 * sizeType : pi + (0+1) * sizeType]
            try:
                unpack(str(dataType), au)
            except:
                return

            u = np.array([unpack(str(dataType), string[pi + j * sizeType: 
                    pi + (j+1) * sizeType])[0] for j in range(amountParams)])[np.newaxis,:]

            if not self.Z[name][index][1].shape[0]: self.Z[name][index][1] = u 
            else: 
                if verbose:
                    print(self.Z[name][index][1].shape, u[:,np.newaxis].shape)
                self.Z[name][index][1] = np.vstack((self.Z[name][index][1], u))
                

        mlen = bufferSize if bufferSize else (6 if plotStyle != "histogram" else 10000000)
        if self.Z[name][index][1].shape[0] > mlen:
            self.Z[name][index] = [plotStyle, self.Z[name][index][1][self.Z[name][index][1].shape[0]-mlen:]]
            assert(self.Z[name][index][1].shape[0] == mlen)
        if verbose: print("->", self.Z[name][index][1].shape, "@\t", "<", name,",", index,">")




    def receiveVal(self, verbose=False):
        string = self.socket.recv()
        c_type = int(string[0])
        if c_type == 0: 
            if verbose: 
                print("logging input:", string)
        else: self.receiveTopics(string, verbose);
        


    def startConnection(self):
        self.address = "tcp://" + self.addr + ":" + str(self.port)

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)
        self.socket.connect(self.address)

        self.socket.setsockopt_string(zmq.SUBSCRIBE, "")

    def run(self):
        while True:
            self.receiveVal()

