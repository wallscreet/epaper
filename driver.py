from ctypes import CDLL
import time
import os
import logging
import sys
import spidev
import gpiozero

# Display resolution
EPD_WIDTH       = 800
EPD_HEIGHT      = 480

GRAY1  = 0xff #white
GRAY2  = 0xC0
GRAY3  = 0x80 #gray
GRAY4  = 0x00 #Blackest

logger = logging.getLogger(__name__)


class RaspberryPi:
    # Pin definition
    RST_PIN  = 17
    DC_PIN   = 25
    CS_PIN   = 8
    BUSY_PIN = 24
    PWR_PIN  = 18
    MOSI_PIN = 10
    SCLK_PIN = 11

    def __init__(self):
        
        
        self.SPI = spidev.SpiDev()
        self.GPIO_RST_PIN    = gpiozero.LED(self.RST_PIN)
        self.GPIO_DC_PIN     = gpiozero.LED(self.DC_PIN)
        # self.GPIO_CS_PIN     = gpiozero.LED(self.CS_PIN)
        self.GPIO_PWR_PIN    = gpiozero.LED(self.PWR_PIN)
        self.GPIO_BUSY_PIN   = gpiozero.Button(self.BUSY_PIN, pull_up = False)

        

    def digital_write(self, pin, value):
        if pin == self.RST_PIN:
            if value:
                self.GPIO_RST_PIN.on()
            else:
                self.GPIO_RST_PIN.off()
        elif pin == self.DC_PIN:
            if value:
                self.GPIO_DC_PIN.on()
            else:
                self.GPIO_DC_PIN.off()
        # elif pin == self.CS_PIN:
        #     if value:
        #         self.GPIO_CS_PIN.on()
        #     else:
        #         self.GPIO_CS_PIN.off()
        elif pin == self.PWR_PIN:
            if value:
                self.GPIO_PWR_PIN.on()
            else:
                self.GPIO_PWR_PIN.off()

    def digital_read(self, pin):
        if pin == self.BUSY_PIN:
            return self.GPIO_BUSY_PIN.value
        elif pin == self.RST_PIN:
            return self.RST_PIN.value
        elif pin == self.DC_PIN:
            return self.DC_PIN.value
        # elif pin == self.CS_PIN:
        #     return self.CS_PIN.value
        elif pin == self.PWR_PIN:
            return self.PWR_PIN.value

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.SPI.writebytes(data)

    def spi_writebyte2(self, data):
        self.SPI.writebytes2(data)

    def DEV_SPI_write(self, data):
        self.DEV_SPI.DEV_SPI_SendData(data)

    def DEV_SPI_nwrite(self, data):
        self.DEV_SPI.DEV_SPI_SendnData(data)

    def DEV_SPI_read(self):
        return self.DEV_SPI.DEV_SPI_ReadData()

    def module_init(self, cleanup=False):
        self.GPIO_PWR_PIN.on()
        
        if cleanup:
            find_dirs = [
                os.path.dirname(os.path.realpath(__file__)),
                '/usr/local/lib',
                '/usr/lib',
            ]
            self.DEV_SPI = None
            for find_dir in find_dirs:
                val = int(os.popen('getconf LONG_BIT').read())
                logging.debug("System is %d bit"%val)
                if val == 64:
                    so_filename = os.path.join(find_dir, 'DEV_Config_64.so')
                else:
                    so_filename = os.path.join(find_dir, 'DEV_Config_32.so')
                if os.path.exists(so_filename):
                    self.DEV_SPI = CDLL(so_filename)
                    break
            if self.DEV_SPI is None:
                RuntimeError('Cannot find DEV_Config.so')

            self.DEV_SPI.DEV_Module_Init()

        else:
            # SPI device, bus = 0, device = 0
            self.SPI.open(0, 0)
            self.SPI.max_speed_hz = 4000000
            self.SPI.mode = 0b00
        return 0

    def module_exit(self, cleanup=False):
        logger.debug("spi end")
        self.SPI.close()

        self.GPIO_RST_PIN.off()
        self.GPIO_DC_PIN.off()
        self.GPIO_PWR_PIN.off()
        logger.debug("close 5V, Module enters 0 power consumption ...")
        
        if cleanup:
            self.GPIO_RST_PIN.close()
            self.GPIO_DC_PIN.close()
            # self.GPIO_CS_PIN.close()
            self.GPIO_PWR_PIN.close()
            self.GPIO_BUSY_PIN.close()


epdconfig = RaspberryPi()


class EPD:
    def __init__(self):
        self.reset_pin = epdconfig.RST_PIN
        self.dc_pin = epdconfig.DC_PIN
        self.busy_pin = epdconfig.BUSY_PIN
        self.cs_pin = epdconfig.CS_PIN
        self.width = EPD_WIDTH
        self.height = EPD_HEIGHT
        self.GRAY1  = GRAY1 #white
        self.GRAY2  = GRAY2
        self.GRAY3  = GRAY3 #gray
        self.GRAY4  = GRAY4 #Blackest

    LUT_DATA_4Gray =  [#  #112bytes										
        0x80,	0x48,	0x4A,	0x22,	0x00,	0x00,	0x00,	0x00,	0x00,	0x00,	
        0x0A,	0x48,	0x68,	0x00,	0x00,	0x00,	0x00,	0x00,	0x00,	0x00,	
        0x88,	0x48,	0x60,	0x00,	0x00,	0x00,	0x00,	0x00,	0x00,	0x00,	
        0xA8,	0x48,	0x45,	0x00,	0x00,	0x00,	0x00,	0x00,	0x00,	0x00,	
        0x00,	0x00,	0x00,	0x00,	0x00,	0x00,	0x00,	0x00,	0x00,	0x00,	
        0x07,	0x1E,	0x1C,	0x02,	0x00,						
        0x05,	0x01,	0x05,	0x01,	0x02,						
        0x08,	0x01,	0x01,	0x04,	0x04,						
        0x00,	0x02,	0x00,	0x02,	0x01,						
        0x00,	0x00,	0x00,	0x00,	0x00,						
        0x00,	0x00,	0x00,	0x00,	0x00,						
        0x00,	0x00,	0x00,	0x00,	0x00,						
        0x00,	0x00,	0x00,	0x00,	0x00,						
        0x00,	0x00,	0x00,	0x00,	0x00,						
        0x00,	0x00,	0x00,	0x00,	0x01,						
        0x22,	0x22,	0x22,	0x22,	0x22,						
        0x17,	0x41,	0xA8,	0x32,	0x30,						
        0x00,	0x00	]
    
    # Hardware reset
    def reset(self):
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(20) 
        epdconfig.digital_write(self.reset_pin, 0)
        epdconfig.delay_ms(2)
        epdconfig.digital_write(self.reset_pin, 1)
        epdconfig.delay_ms(20)   

    def send_command(self, command):
        epdconfig.digital_write(self.dc_pin, 0)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([command])
        epdconfig.digital_write(self.cs_pin, 1)

    def send_data(self, data):
        epdconfig.digital_write(self.dc_pin, 1)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.spi_writebyte([data])
        epdconfig.digital_write(self.cs_pin, 1)

    def send_data2(self, data):
        epdconfig.digital_write(self.dc_pin, 1)
        epdconfig.digital_write(self.cs_pin, 0)
        epdconfig.SPI.writebytes2(data)
        epdconfig.digital_write(self.cs_pin, 1)

    def ReadBusy(self):
        logger.debug("e-Paper busy")
        busy = epdconfig.digital_read(self.busy_pin)
        while(busy == 1):
            busy = epdconfig.digital_read(self.busy_pin)
            epdconfig.delay_ms(20)
        epdconfig.delay_ms(20)
        logger.debug("e-Paper busy release")

    def TurnOnDisplay(self):
        self.send_command(0x22) #Display Update Control
        self.send_data(0xF7)
        self.send_command(0x20) #Activate Display Update Sequence
        self.ReadBusy()

    def TurnOnDisplay_Fast(self):
        self.send_command(0x22) #Display Update Control
        self.send_data(0xC7)
        self.send_command(0x20) #Activate Display Update Sequence
        self.ReadBusy()

    def TurnOnDisplay_Part(self):
        self.send_command(0x22) #Display Update Control
        self.send_data(0xFF)
        self.send_command(0x20) #Activate Display Update Sequence
        self.ReadBusy()

    def TurnOnDisplay_4GRAY(self):
        self.send_command(0x22) #Display Update Control
        self.send_data(0xC7)
        self.send_command(0x20) #Activate Display Update Sequence
        self.ReadBusy()

    '''
    function : Setting the display window
    parameter:
        xstart : X-axis starting position
        ystart : Y-axis starting position
        xend : End position of X-axis
        yend : End position of Y-axis
    '''
    def SetWindow(self, x_start, y_start, x_end, y_end):
        self.send_command(0x44) # SET_RAM_X_ADDRESS_START_END_POSITION
        self.send_data(x_start & 0xFF)
        self.send_data((x_start>>8) & 0x03)
        self.send_data(x_end & 0xFF)
        self.send_data((x_end>>8) & 0x03)
        
        self.send_command(0x45) # SET_RAM_Y_ADDRESS_START_END_POSITION
        self.send_data(y_start & 0xFF)
        self.send_data((y_start >> 8) & 0xFF)
        self.send_data(y_end & 0xFF)
        self.send_data((y_end >> 8) & 0xFF)

    '''
    function : Set Cursor
    parameter:
        x : X-axis starting position
        y : Y-axis starting position
    '''
    def SetCursor(self, x, y):
        self.send_command(0x4E) # SET_RAM_X_ADDRESS_COUNTER
        # x point must be the multiple of 8 or the last 3 bits will be ignored
        self.send_data(x & 0xFF)
        self.send_data((x>>8) & 0x03)
        
        self.send_command(0x4F) # SET_RAM_Y_ADDRESS_COUNTER
        self.send_data(y & 0xFF)
        self.send_data((y >> 8) & 0xFF)
        
    def init(self):
        if (epdconfig.module_init() != 0):
            return -1
        # EPD hardware init start
        self.reset()
        self.ReadBusy()

        self.send_command(0x12) #SWRESET
        self.ReadBusy()

        self.send_command(0x18) # use the internal temperature sensor
        self.send_data(0x80)

        self.send_command(0x0C) #set soft start     
        self.send_data(0xAE)
        self.send_data(0xC7)
        self.send_data(0xC3)
        self.send_data(0xC0)
        self.send_data(0x80)

        self.send_command(0x01)   #      drive output control    
        self.send_data((self.height-1)%256) #  Y  
        self.send_data((self.height-1)//256) #  Y 
        self.send_data(0x02)

        self.send_command(0x3C)        # Border       Border setting 
        self.send_data(0x01)

        self.send_command(0x11)        #    data  entry  mode
        self.send_data(0x01)           #       X-mode  x+ y-    

        self.SetWindow(0, self.height-1, self.width-1, 0)

        self.SetCursor(0, 0)
        self.ReadBusy()

        # EPD hardware init end
        return 0
    
    def init_Fast(self):
        if (epdconfig.module_init() != 0):
            return -1
        # EPD hardware init start
        self.reset()
        self.ReadBusy()

        self.send_command(0x12) #SWRESET
        self.ReadBusy()
        
        self.send_command(0x18) # use the internal temperature sensor
        self.send_data(0x80)

        self.send_command(0x0C) #set soft start     
        self.send_data(0xAE)
        self.send_data(0xC7)
        self.send_data(0xC3)
        self.send_data(0xC0)
        self.send_data(0x80)

        self.send_command(0x01)   #      drive output control    
        self.send_data((self.height-1)%256) #  Y  
        self.send_data((self.height-1)//256) #  Y 
        self.send_data(0x02)

        self.send_command(0x3C)        # Border       Border setting 
        self.send_data(0x01)

        self.send_command(0x11)        #    data  entry  mode
        self.send_data(0x01)           #       X-mode  x+ y-    

        self.SetWindow(0, self.height-1, self.width-1, 0)

        self.SetCursor(0, 0)
        self.ReadBusy()

        #TEMP (1.5s)
        self.send_command(0x1A)  
        self.send_data(0x5A) 

        self.send_command(0x22)  
        self.send_data(0x91) 
        self.send_command(0x20) 
        
        self.ReadBusy()

        # EPD hardware init end
        return 0

    def Lut(self):
        self.send_command(0x32)
        for count in range(0, 105):
            self.send_data(self.LUT_DATA_4Gray[count])

        self.send_command(0x03) #VGH      
        self.send_data(self.LUT_DATA_4Gray[105])

        self.send_command(0x04) #      
        self.send_data(self.LUT_DATA_4Gray[106]) #VSH1   
        self.send_data(self.LUT_DATA_4Gray[107]) #VSH2   
        self.send_data(self.LUT_DATA_4Gray[108]) #VSL   

        self.send_command(0x2C)     #VCOM Voltage
        self.send_data(self.LUT_DATA_4Gray[109])    #0x1C

    def init_4GRAY(self):
        if (epdconfig.module_init() != 0):
            return -1
        # EPD hardware init start
        self.reset()
        self.ReadBusy()

        self.send_command(0x12) #SWRESET
        self.ReadBusy()
        
        self.send_command(0x18) # use the internal temperature sensor
        self.send_data(0x80)

        self.send_command(0x0C) #set soft start     
        self.send_data(0xAE)
        self.send_data(0xC7)
        self.send_data(0xC3)
        self.send_data(0xC0)
        self.send_data(0x80)

        self.send_command(0x01)   #      drive output control    
        self.send_data((self.height-1)%256) #  Y  
        self.send_data((self.height-1)//256) #  Y 
        self.send_data(0x02)

        self.send_command(0x3C)        # Border       Border setting 
        self.send_data(0x01)

        self.send_command(0x11)        #    data  entry  mode
        self.send_data(0x01)           #       X-mode  x+ y-    

        self.SetWindow(0, self.height-1, self.width-1, 0)

        self.SetCursor(0, 0)
        self.ReadBusy()

        self.Lut()
        # EPD hardware init end
        return 0


    def getbuffer(self, image):
        # logger.debug("bufsiz = ",int(self.width/8) * self.height)
        buf = [0xFF] * (int(self.width / 8) * self.height)
        image_monocolor = image.convert('1')
        imwidth, imheight = image_monocolor.size
        pixels = image_monocolor.load()
        # logger.debug("imwidth = %d, imheight = %d",imwidth,imheight)
        if imwidth == self.width and imheight == self.height:
            logger.debug("Horizontal")
            for y in range(imheight):
                for x in range(imwidth):
                    # Set the bits for the column of pixels at the current position.
                    if pixels[x, y] == 0:
                        buf[int((x + y * self.width) / 8)] &= ~(0x80 >> (x % 8))
        elif imwidth == self.height and imheight == self.width:
            logger.debug("Vertical")
            for y in range(imheight):
                for x in range(imwidth):
                    newx = y
                    newy = self.height - x - 1
                    if pixels[x, y] == 0:
                        buf[int((newx + newy * self.width) / 8)] &= ~(0x80 >> (y % 8))
        return buf
    
    def getbuffer_4Gray(self, image):
        # logger.debug("bufsiz = ",int(self.width/8) * self.height)
        buf = [0xFF] * (int(self.width / 4) * self.height)
        image_monocolor = image.convert('L')
        imwidth, imheight = image_monocolor.size
        pixels = image_monocolor.load()
        i=0
        # logger.debug("imwidth = %d, imheight = %d",imwidth,imheight)
        if(imwidth == self.width and imheight == self.height):
            logger.debug("Vertical")
            for y in range(imheight):
                for x in range(imwidth):
                    # Set the bits for the column of pixels at the current position.
                    if(pixels[x, y] == 0xC0):
                        pixels[x, y] = 0x80
                    elif (pixels[x, y] == 0x80):
                        pixels[x, y] = 0x40
                    i= i+1
                    if(i%4 == 0):
                        buf[int((x + (y * self.width))/4)] = ((pixels[x-3, y]&0xc0) | (pixels[x-2, y]&0xc0)>>2 | (pixels[x-1, y]&0xc0)>>4 | (pixels[x, y]&0xc0)>>6)
                        
        elif(imwidth == self.height and imheight == self.width):
            logger.debug("Horizontal")
            for x in range(imwidth):
                for y in range(imheight):
                    newx = y
                    newy = self.height - x - 1
                    if(pixels[x, y] == 0xC0):
                        pixels[x, y] = 0x80
                    elif (pixels[x, y] == 0x80):
                        pixels[x, y] = 0x40
                    i= i+1
                    if(i%4 == 0):
                        buf[int((newx + (newy * self.width))/4)] = ((pixels[x, y-3]&0xc0) | (pixels[x, y-2]&0xc0)>>2 | (pixels[x, y-1]&0xc0)>>4 | (pixels[x, y]&0xc0)>>6) 
        return buf

    def display(self, image):
        self.send_command(0x24)
        self.send_data2(image)

        self.TurnOnDisplay()

    def display_Base(self, image):
        self.send_command(0x24)
        self.send_data2(image)

        self.send_command(0x26)
        self.send_data2(image)

        self.TurnOnDisplay()

    def display_Fast(self, image):
        self.send_command(0x24)
        self.send_data2(image)

        self.TurnOnDisplay_Fast()

    def display_Partial(self, Image):
        
        # Reset
        self.reset()

        self.send_command(0x18) #BorderWavefrom
        self.send_data(0x80)

        self.send_command(0x3C) #BorderWavefrom
        self.send_data(0x80)

        self.send_command(0x01)   #      drive output control    
        self.send_data((self.height-1)%256) #  Y  
        self.send_data((self.height-1)//256) #  Y 

        self.send_command(0x11)        #    data  entry  mode
        self.send_data(0x01)           #       X-mode  x+ y-    

        self.SetWindow(0, self.height-1, self.width-1, 0)

        self.SetCursor(0, 0)

        self.send_command(0x24)   #Write Black and White image to RAM
        self.send_data2(Image)

        self.TurnOnDisplay_Part()

    def display_4Gray(self, image):
        self.send_command(0x24)
        for i in range(0, 48000):                     #5808*4  46464
            temp3=0
            for j in range(0, 2):
                temp1 = image[i*2+j]
                for k in range(0, 2):
                    temp2 = temp1&0xC0 
                    if(temp2 == 0xC0):
                        temp3 |= 0x00
                    elif(temp2 == 0x00):
                        temp3 |= 0x01  
                    elif(temp2 == 0x80): 
                        temp3 |= 0x01 
                    else: #0x40
                        temp3 |= 0x00 
                    temp3 <<= 1	
                    
                    temp1 <<= 2
                    temp2 = temp1&0xC0 
                    if(temp2 == 0xC0): 
                        temp3 |= 0x00
                    elif(temp2 == 0x00): 
                        temp3 |= 0x01
                    elif(temp2 == 0x80):
                        temp3 |= 0x01
                    else :   #0x40
                        temp3 |= 0x00	
                    if(j!=1 or k!=1):				
                        temp3 <<= 1
                    temp1 <<= 2
            self.send_data(temp3)
            
        self.send_command(0x26)	       
        for i in range(0, 48000):                #5808*4  46464
            temp3=0
            for j in range(0, 2):
                temp1 = image[i*2+j]
                for k in range(0, 2):
                    temp2 = temp1&0xC0 
                    if(temp2 == 0xC0):
                        temp3 |= 0x00
                    elif(temp2 == 0x00):
                        temp3 |= 0x01
                    elif(temp2 == 0x80):
                        temp3 |= 0x00
                    else: #0x40
                        temp3 |= 0x01 
                    temp3 <<= 1	
                    
                    temp1 <<= 2
                    temp2 = temp1&0xC0 
                    if(temp2 == 0xC0): 
                        temp3 |= 0x00
                    elif(temp2 == 0x00): 
                        temp3 |= 0x01
                    elif(temp2 == 0x80):
                        temp3 |= 0x00 
                    else:    #0x40
                            temp3 |= 0x01	
                    if(j!=1 or k!=1):					
                        temp3 <<= 1
                    temp1 <<= 2
            self.send_data(temp3)
        
        self.TurnOnDisplay_4GRAY()

    def Clear(self):
        self.send_command(0x24)
        self.send_data2([0xFF] * (int(self.width/8) * self.height))

        self.send_command(0x26)
        self.send_data2([0xFF] * (int(self.width/8) * self.height))

        self.TurnOnDisplay()

    def sleep(self):
        self.send_command(0x10) # DEEP_SLEEP
        self.send_data(0x01)
        
        epdconfig.delay_ms(2000)
        epdconfig.module_exit()