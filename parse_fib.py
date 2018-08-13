#!/usr/bin/env python

from __future__ import print_function
import crcmod
from bitstring import BitStream, BitArray
from jdcal import jd2gcal

def bytes_from_file(filename, chunksize=32):
    with open(filename, "rb") as f:
        while True:
            chunk = f.read(chunksize)
            if chunk:
                yield chunk
            else:
                break

mycrc=crcmod.predefined.mkCrcFun('crc-16-genibus')

for b in bytes_from_file('test.fib',32):
    print()
    print("New FIB:")
    crc=ord(b[30])*256+ord(b[31])
    if (crc != mycrc(b[0:30])):
        print( "CRC failed, skipping.","crc:",crc,"calc:",mycrc(b[0:30]))
        continue
    b=b[0:30]
    while len(b)>0:
#        print "blen=",len(b)
        a= BitStream(bytes=b)
        type=a.read('uint:3')
        length=a.read('uint:5')
        if (type==7) and (length==31):
            print("- END")
            break
        if length==0 or length>len(b):
            print("invalid length ",length,len(b))
            next
#        print("- len: ",length)
        if type==0:
            cn=a.read('uint:1')
            oe=a.read('uint:1')
            pd=a.read('uint:1')
            subtype=a.read('uint:5')

#            print("- FIG %d/%d"%(type,subtype)," (C/N:%d OE:%d P/D:%d)"%(cn,oe,pd))
            print("- FIG %d/%d"%(type,subtype))
            if subtype==10: # time
                if cn!=0:
                    print("! cn !=0",cn)
                if oe!=0:
                    print("! oe !=0",oe)
                if pd!=0:
                    print("! pd !=0",pd)
                rfu=a.read('uint:1')
                if rfu!=0:
                    print("! rfu !=0",rfu)
                MJD=a.read('uint:17')
                (year,month,day,_)=jd2gcal(2400000.5, MJD)
                lsi=a.read('uint:1')
                if lsi!=0:
                    print("  leap second imminent",lsi)
                rfa=a.read('uint:1')
                if rfa!=0:
                    print("! rfa !=0",rfa)
                utc=a.read('uint:1')
                hh=a.read('uint:5')
                mm=a.read('uint:6')
                if utc:
                    ss=a.read('uint:6')
                    uu=a.read('uint:10')
                    print ("  Date: %04d-%02d-%02d %02d:%02d:%02d.%03d"%(year,month,day,hh,mm,ss,uu))
                else:
                    print ("  Date: %04d-%02d-%02d %02d:%02d"%(year,month,day,hh,mm))

            elif subtype==0: # Ensemble
                if cn!=0:
                    print("! cn !=0",cn)
                if oe!=0:
                    print("! oe !=0",oe)
                if pd!=0:
                    print("! pd !=0",pd)
                eid_cc=a.read('uint:4')
                eid_er=a.read('uint:12')
                cf=a.read('uint:2')
                al=a.read('uint:1')
                cif1=a.read('uint:5')
                cif2=a.read('uint:8')
                oc=a.read('uint:8')
                print("  Ensemble: %d/%d"%(eid_cc,eid_er),"  Change: %d, Alarms allowed: %d"%(cf,al))
                print("  CIF: %02d/%03d"%(cif1,cif2))

            else:
                print("+",b[2:length+1].encode('hex'))
            
        elif type==1:
            print("- FIG",type,"(Labels, etc.)")
            charset=a.read('uint:4')
            rfu=a.read('uint:1')
            extension=a.read('uint:3')
            if charset!=0:
                print("! Charset !=0",charset)
            if rfu!=0:
                print("! rfu !=0",rfu)
            if extension!=0:
                print("! extension !=0",extension)
            identifier=a.read('uint:16') # XXX: unclear, depend on extension?
            text=a.read('bytes:16')
            flags=a.read('bin:16')
            shorttext=""
            for (num,c) in enumerate(text):
                if flags[num] == '1': shorttext+=c
            print("  Text: \"%s\" [%s]"%(text,shorttext))
        else:
            print("- type: ",type)
            print("+",b[1:length+1].encode('hex'))
        b=b[length+1:]
#        print "rest len: ",len(b)
    print("")
