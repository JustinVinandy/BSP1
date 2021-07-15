import os
import sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from bitstring import BitArray 
from PIL import Image

cont='Y'                     #low add more noise #low  interface
                            #(low) file or message
while cont=='Y':
        ans= str(input('\nWhat do you want to do: encrypt("E") or decrypt("D") :'))
        if ans == 'E' :
                backend = default_backend()
                salt = b'This is fixed'  
                nonce = os.urandom(12) 
                non=BitArray(nonce)
                aad = b""    #bascically useless

                kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                     length=32,
                     salt=salt,
                     iterations=100000,
                     backend=backend)

                datab = str(input('Give message : '))
                typ=datab[-3:] 
                data=open(datab,'rb').read()

                password = bytes(input('Give password : '),'utf-8')
                key = kdf.derive(password)
  
                aesgcm = AESGCM(key)
                ct = aesgcm.encrypt(nonce, data, b'')
                temp=BitArray(ct)

                tl=str(len(temp.bin))
                typtl=bytes(typ+tl,'utf-8')  
                tem=BitArray(typtl)
                while len(tem.bin) < 128:
                        tem.prepend('0b1')
                
                nonce2=os.urandom(12)
                non2=BitArray(nonce2)
                ty = aesgcm.encrypt(nonce2, tem.bytes, aad)  #this is 32 bytes long
                typ=BitArray(ty)

                im = Image.open('blue clouds.png').convert("RGBA")
                width, height = im.size
                n=0
                for i in range(width):
                        for j in range(height):      #maybe it's possible to write this neater
                            r,g,b,a = im.getpixel((i,j))                
                            red=BitArray(int=r ,length=9)
                            green=BitArray(int=g ,length=9)
                            blue=BitArray(int=b ,length=9)
                            alpha=BitArray(int=a, length=9)
                            print(red.bin)
                            if n < 96 :
                             red.bin  =red.bin[:-1]+non.bin[n]
                             green.bin=green.bin[:-1]+non.bin[n+1]
                             blue.bin =blue.bin[:-1]+non.bin[n+2]
                             alpha.bin =alpha.bin[:-1]+non.bin[n+3]
                            elif n >= 96 and n < 192 :
                             red.bin  =red.bin[:-1]+non2.bin[n-96]
                             green.bin=green.bin[:-1]+non2.bin[n+1-96]
                             blue.bin =blue.bin[:-1]+non2.bin[n+2-96]
                             alpha.bin =alpha.bin[:-1]+non2.bin[n+3-96]
                            elif n >= 192 and n < 192+256 :
                             red.bin  =red.bin[:-1]+typ.bin[n-192]
                             green.bin=green.bin[:-1]+typ.bin[n+1-192]
                             blue.bin =blue.bin[:-1]+typ.bin[n+2-192]
                             alpha.bin =alpha.bin[:-1]+typ.bin[n+3-192]
                            elif n>=192+256 and n+3 <= len(temp.bin)+192+256 :
                             red.bin  =red.bin[:-1]+temp.bin[n-(192+256)]
                             green.bin=green.bin[:-1]+temp.bin[n+1-(192+256)]
                             blue.bin =blue.bin[:-1]+temp.bin[n+2-(192+256)]
                             alpha.bin =alpha.bin[:-1]+temp.bin[n+3-(192+256)]
                            else:
                                    break
                            n=n+4
                            im.putpixel((i,j), (red.int ,green.int,blue.int,alpha.int))
                              
                im.save('myimage.png')
                print('image saved as myimage.png')
                cont=str(input('Do you want to continue? (Y/N) : '))

        elif ans == 'D' :
                backend = default_backend()
                salt = b'This is fixed'  
                gim = Image.open(input('What image do you want to decrypt :')).convert("RGBA")

                kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                     length=32,
                     salt=salt,
                     iterations=100000,
                     backend=backend)
                pass2 = bytes(input('Whats the password : '),'utf-8')
                key2 = kdf.derive(pass2)
                aesgcm = AESGCM(key2)
                
                width, height = gim.size
                gnon2 = BitArray()
                gnon=BitArray()
                gtyp=BitArray()
                leng=0
                m=0
                z=''
                for i in range(width):
                        for j in range(height):       
                            r,g,b,a = gim.getpixel((i,j))                  
                            red=BitArray(int=r ,length=9)
                            green=BitArray(int=g ,length=9)
                            blue=BitArray(int=b ,length=9)
                            alpha=BitArray(int=a, length=9)
                            if m < 96 :
                             z += red.bin[-1]
                             z += green.bin[-1]
                             z += blue.bin[-1]
                             z += alpha.bin[-1]
                             gnon.bin += z 
                             z=''
                            elif m >= 96 and m < 192 :
                             z += red.bin[-1]
                             z += green.bin[-1]
                             z += blue.bin[-1]
                             z += alpha.bin[-1]
                             gnon2.bin += z 
                             z=''
                            elif m >= 192 and m < 192+256 :
                             z += red.bin[-1]
                             z += green.bin[-1]
                             z += blue.bin[-1]
                             z += alpha.bin[-1]
                             gtyp.bin += z
                             z=''
                             if len(gtyp.bin) == 256 :
                                     typ2=aesgcm.decrypt(gnon2.bytes,gtyp.bytes , b'')
                                     tem=BitArray(typ2)
                                     tem.replace('0xff' ,'')
                                     leng=int(tem.bytes[3:])
                                     gmess=BitArray(length=leng)
                            elif m>=192+256 and m+3 <= leng +192+256 :
                             gmess.set(int(red.bin[-1]),m-(192+256))
                             gmess.set(int(green.bin[-1]),m+1-(192+256))
                             gmess.set(int(blue.bin[-1]),m+2-(192+256))
                             gmess.set(int(alpha.bin[-1]),m+3-(192+256))
                            else:
                                    break
                            m=m+4

                pt=aesgcm.decrypt(gnon.bytes,gmess.bytes , b'')
                f=open('hiddenmessage.'+ tem.bytes[0:3].decode('utf-8') ,'wb+')
                f.write(pt)
                f.close()
                cont=str(input('Do you want to continue? (Y/N) : '))
        else:
                print('Please write either E or D for what you want to use. ')
                cont='Y'



