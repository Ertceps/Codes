# --------------------------------------
# SENSORS - INPUTS
# --------------------------------------

# -+- IMPORT -+-
import time
# import RPi.GPIO as GPIO
import platform
from ctypes.test import usage
if platform.system() == 'Windows':
    pass
else:
    import GPIO
import threading


class Sensors:
    """uses delegation to windows- or raspberry-Implementation """

    def __init__(self):
        if platform.system() == 'Windows':
            self.delegate = SensorsWindows()
        else:
            self.delegate = SensorsRaspberry()
    def stop(self):
        self.delegate.stop()


class SensorsWindows:
    def __init__(self):
        self.queue = queue

        self._stop = threading.Event()
        self.thread = threading.Thread(target=self.run)
        self.thread.setName("SensorsWindows")
        self._stop.clear()
        self.thread.start()

    def run(self):
        while not self._stop.isSet():
            time.sleep(0.05)  # small delay to prevent excessive CPU usage
            s = raw_input("your action ")
            if s == 'pp_on':
                self.queue.put("pp_on")
            elif s == 'pp_off':
                self.queue.put("pp_off")
            elif s == 'tmp_on':
                self.queue.put("tmp_on")
            elif s == 'tmp_off':
                self.queue.put("tmp_off")
            elif s == 'hvgv_on':
                self.queue.put("hvgv_on")
            elif s == 'hvgv_off':
                self.queue.put("hvgv_off")
            elif s == 'vv_on':
                self.queue.put("vv_on")
            elif s == 'vv_off':
                self.queue.put("vv_off")
            elif s == 'VC_vent':
                self.queue.put("VC_vent")
            elif s == 'VC_vacuum':
                self.queue.put("VC_vacuum")
            elif s == 'local':
                self.queue.put("local")
            # needed for simulating shutdown
            elif s == 'stop':
                self.queue.put("stop")
            else:
                print ("unknown input")

    def stop(self):
        self._stop.set()


class SensorsRaspberry:

    # change these as desired - they're the pins connected from the SPI port on the ADC to the Cobbler
    spiclk = 11  # Rpi.GPIO pin - Serial Clock (output from master) - Real pin #23 Rpi
    spimiso = 9  # Master Input, Slave Output (output from slave) - Real pin #21 Rpi
    spimosi = 10  # Master Output, Slave Input (output from master) - Real pin #19 Rpi
    spics = 7  # Chip Select - Real pin #26 Rpi

    # Sensors ADC Channels
    pirani_p1_pin = 0  # Pirani 1 connected to adc #0
    cold_cathod_p2_pin = 1  # Cold cathod connected to adc #1
    pirani_p3_pin = 2  # Pirani 2 connected to adc #2

    def __init__(self):

        # set up the SPI interface pins
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(spimosi, GPIO.OUT)
        GPIO.setup(spimiso, GPIO.IN)
        GPIO.setup(spiclk, GPIO.OUT)
        GPIO.setup(spics, GPIO.OUT)

        print("Sensors pins setup")

        self._stop = threading.Event()
        self.thread = threading.Thread(target=self.run)
        self.thread.setName("SensorsRaspberry")
        self._stop.clear()
        self.thread.start()

    def run(self):

        while not self._stop.isSet():  # endless loop to read buttons
            p1 = readadc(pirani_p1_pin, spiclk, spimiso, spimosi, spics)
            sensors[1] = p1 / 65.536
            print 'P1 = {p1}%' .format(p1=P1)
            p2 = readadc(cold_cathod_p2_pin, spiclk, spimiso, spimosi, spics)
            sensors[2] = p2 / 65.536
            print 'P2 = {p2}%' .format(p2=P2)
            p3 = readadc(pirani_p3_pin, spiclk, spimiso, spimosi, spics)
            sensors[3] = p3 / 65.536
            print 'P3 = {p3}%' .format(p3=P3)
            timestamp_sensors = time.time()
            self.app.setPressure(sensors)
            time.sleep(1)  # Get data every 1 sec frequency 1Hz
            print "%s"
            time.sleep(0.05)  # small delay to prevent excessive CPU usage

    def stop(self):
        self._stop.set()



# ===========================================================================
# ADS1118 Class
# ===========================================================================
__all__ = ['ADS1118']
class ADS1118:
    i2c = None

    # IC Identifiers
    __IC_ADS1118 = 0x01

    # Config Register
    __ADS1118_REG_CONFIG_DR_8SPS      = 0x0000  # 8 samples per second
    __ADS1118_REG_CONFIG_DR_16SPS     = 0x0020  # 16 samples per second
    __ADS1118_REG_CONFIG_DR_32SPS     = 0x0040  # 32 samples per second
    __ADS1118_REG_CONFIG_DR_64SPS     = 0x0060  # 64 samples per second
    __ADS1118_REG_CONFIG_DR_128SPS    = 0x0080  # 128 samples per second
    __ADS1118_REG_CONFIG_DR_250SPS    = 0x00A0  # 250 samples per second (default)
    __ADS1118_REG_CONFIG_DR_475SPS    = 0x00C0  # 475 samples per second
    __ADS1118_REG_CONFIG_DR_860SPS    = 0x00E0  # 860 samples per second

    __ADS1118_REG_CONFIG_CQUE_MASK    = 0x0003
    __ADS1118_REG_CONFIG_CQUE_1CONV   = 0x0000  # Assert ALERT/RDY after one conversions
    __ADS1118_REG_CONFIG_CQUE_2CONV   = 0x0001  # Assert ALERT/RDY after two conversions
    __ADS1118_REG_CONFIG_CQUE_4CONV   = 0x0002  # Assert ALERT/RDY after four conversions
    __ADS1118_REG_CONFIG_CQUE_NONE    = 0x0003  # Disable the comparator and put ALERT/RDY in high state (default)

    __ADS1118_REG_CONFIG_CMODE_MASK   = 0x0010
    __ADS1118_REG_CONFIG_CMODE_TRAD   = 0x0000  # Traditional comparator with hysteresis (default)
    __ADS1118_REG_CONFIG_CMODE_WINDOW = 0x0010  # Window comparator

    __ADS1118_REG_CONFIG_CPOL_MASK    = 0x0008
    __ADS1118_REG_CONFIG_CPOL_ACTVLOW = 0x0000  # ALERT/RDY pin is low when active (default)
    __ADS1118_REG_CONFIG_CPOL_ACTVHI  = 0x0008  # ALERT/RDY pin is high when active

    __ADS1118_REG_CONFIG_CLAT_MASK    = 0x0004  # Determines if ALERT/RDY pin latches once asserted
    __ADS1118_REG_CONFIG_CLAT_NONLAT  = 0x0000  # Non-latching comparator (default)
    __ADS1118_REG_CONFIG_CLAT_LATCH   = 0x0004  # Latching comparator

    __ADS1118_REG_CONFIG_MODE_MASK    = 0x0100
    __ADS1118_REG_CONFIG_MODE_CONTIN  = 0x0000  # Continuous conversion mode
    __ADS1118_REG_CONFIG_MODE_SINGLE  = 0x0100  # Power-down single-shot mode (default)

    __ADS1118_REG_CONFIG_PGA_MASK     = 0x0E00
    __ADS1118_REG_CONFIG_PGA_6_144V   = 0x0000  # +/-6.144V range
    __ADS1118_REG_CONFIG_PGA_4_096V   = 0x0200  # +/-4.096V range
    __ADS1118_REG_CONFIG_PGA_2_048V   = 0x0400  # +/-2.048V range (default)
    __ADS1118_REG_CONFIG_PGA_1_024V   = 0x0600  # +/-1.024V range
    __ADS1118_REG_CONFIG_PGA_0_512V   = 0x0800  # +/-0.512V range
    __ADS1118_REG_CONFIG_PGA_0_256V   = 0x0A00  # +/-0.256V range

    __ADS1118_REG_CONFIG_MUX_MASK     = 0x7000
    __ADS1118_REG_CONFIG_MUX_DIFF_0_1 = 0x0000  # Differential P = AIN0, N = AIN1 (default)
    __ADS1118_REG_CONFIG_MUX_DIFF_0_3 = 0x1000  # Differential P = AIN0, N = AIN3
    __ADS1118_REG_CONFIG_MUX_DIFF_1_3 = 0x2000  # Differential P = AIN1, N = AIN3
    __ADS1118_REG_CONFIG_MUX_DIFF_2_3 = 0x3000  # Differential P = AIN2, N = AIN3
    __ADS1118_REG_CONFIG_MUX_SINGLE_0 = 0x4000  # Single-ended AIN0
    __ADS1118_REG_CONFIG_MUX_SINGLE_1 = 0x5000  # Single-ended AIN1
    __ADS1118_REG_CONFIG_MUX_SINGLE_2 = 0x6000  # Single-ended AIN2
    __ADS1118_REG_CONFIG_MUX_SINGLE_3 = 0x7000  # Single-ended AIN3

     # Config Register
    __ADS1118_REG_CONFIG_OS_MASK      = 0x8000
    __ADS1118_REG_CONFIG_OS_SINGLE    = 0x8000  # Write: Set to start a single-conversion
    __ADS1118_REG_CONFIG_OS_BUSY      = 0x0000  # Read: Bit = 0 when conversion is in progress
    __ADS1118_REG_CONFIG_OS_NOTBUSY   = 0x8000  # Read: Bit = 1 when device is not performing a conversion

    # Pointer Register
    __ADS1118_REG_POINTER_MASK        = 0x03
    __ADS1118_REG_POINTER_CONVERT     = 0x00
    __ADS1118_REG_POINTER_CONFIG      = 0x01
    __ADS1118_REG_POINTER_LOWTHRESH   = 0x02
    __ADS1118_REG_POINTER_HITHRESH    = 0x03

    # Dictionaries with the sampling speed values
    # These simplify and clean the code (avoid the abuse of if/elif/else clauses)
    spsADS1118 = {
        8:__ADS1118_REG_CONFIG_DR_8SPS,
        16:__ADS1118_REG_CONFIG_DR_16SPS,
        32:__ADS1118_REG_CONFIG_DR_32SPS,
        64:__ADS1118_REG_CONFIG_DR_64SPS,
        128:__ADS1118_REG_CONFIG_DR_128SPS,
        250:__ADS1118_REG_CONFIG_DR_250SPS,
        475:__ADS1118_REG_CONFIG_DR_475SPS,
        860:__ADS1118_REG_CONFIG_DR_860SPS
        }

    # Dictionary with the programmable gains
    pgaADS1x18 = {
        6144:__ADS1118_REG_CONFIG_PGA_6_144V,
        4096:__ADS1118_REG_CONFIG_PGA_4_096V,
        2048:__ADS1118_REG_CONFIG_PGA_2_048V,
        1024:__ADS1118_REG_CONFIG_PGA_1_024V,
        512:__ADS1118_REG_CONFIG_PGA_0_512V,
        256:__ADS1118_REG_CONFIG_PGA_0_256V
        }

    # Constructor
    def __init__(self, address=0x48, ic=__IC_ADS1118, debug=False):

        self.address = address
        self.debug = debug

        # Make sure the IC specified is valid
        if (ic > self.__IC_ADS1118):
            return -1
        else:
            self.ic = ic

        # Set pga value, so that getLastConversionResult() can use it,
        # any function that accepts a pga value must update this.
        self.pga = 6144


# read SPI data from chip, 4 possible adc's (0 to 3)
def readadc(self, channel, clockpin, mosipin, misopin, cspin, pga=6144, sps=250):
        if (channel > 3) or (channel < 0):
                return -1

        # Disable comparator, Non-latching, Alert/Rdy active low
        # traditional comparator, single-shot mode
        config = self.__ADS1118_REG_CONFIG_CQUE_NONE    | \
                 self.__ADS1118_REG_CONFIG_CLAT_NONLAT  | \
                 self.__ADS1118_REG_CONFIG_CPOL_ACTVLOW | \
                 self.__ADS1118_REG_CONFIG_CMODE_TRAD   | \
                 self.__ADS1118_REG_CONFIG_MODE_SINGLE

        # Set sample per seconds, defaults to 250sps
        config |= self.spsADS1118.setdefault(sps, self.__ADS1118_REG_CONFIG_DR_250SPS)

        # Set PGA/voltage range, defaults to +-6.144V
        config |= self.pgaADS1x18.setdefault(pga, self.__ADS1118_REG_CONFIG_PGA_6_144V)
        self.pga = pga

        # Set the channel to be converted
        if channel == 3:
            config |= self.__ADS1118_REG_CONFIG_MUX_SINGLE_3
        elif channel == 2:
            config |= self.__ADS1118_REG_CONFIG_MUX_SINGLE_2
        elif channel == 1:
            config |= self.__ADS1118_REG_CONFIG_MUX_SINGLE_1
        else:
            config |= self.__ADS1118_REG_CONFIG_MUX_SINGLE_0

        # Set 'start single-conversion' bit
        config |= self.__ADS1118_REG_CONFIG_OS_SINGLE

        # Write config register to the ADC
        bytes = [(config >> 8) & 0xFF, config & 0xFF]
        self.i2c.write_i2c_block_data(self.address, self.__ADS1118_REG_POINTER_CONFIG, bytes)  #!!!!!!!!!!!!! I2C nike t mort

        # Wait for the ADC conversion to complete
        # The minimum delay depends on the sps: delay >= 1/sps
        # We add 0.1ms to be sure
        delay = 1.0/sps+0.0001
        time.sleep(delay)

        # Read the conversion results
        result = self.i2c.read_i2c_block_data(self.address, self.__ADS1118_REG_POINTER_CONVERT, 2)    #!!!!!!!!!!!!! I2C nike t mort
        # Return a mV value for the ADS1118
        # (Take signed values into account as well)
        val = (result[0] << 8) | (result[1])
        if val > 0x7FFF:
            return (val - 0xFFFF)*pga/32768.0
        else:
            return ( (result[0] << 8) | (result[1]) )*pga/32768.0

        # GPIO.output(cspin, True)

        # GPIO.output(clockpin, False)  # start clock low
        # GPIO.output(cspin, False)     # bring CS low
        #
        # commandout = channel
        # commandout |= 0x18  # start bit + single-ended bit
        # commandout <<= 3    # we need to send 16 bits here
        # for i in range(16):
        #         if commandout & 0x80:
        #                 GPIO.output(mosipin, True)
        #         else:
        #                 GPIO.output(mosipin, False)
        #         commandout <<= 1
        #         GPIO.output(clockpin, True)
        #         GPIO.output(clockpin, False)
        #
        # adcout = 0
        # # read in one empty bit, one null bit and 10 ADC bits
        # for i in range(12):
        #         GPIO.output(clockpin, True)
        #         GPIO.output(clockpin, False)
        #         adcout <<= 1
        #         if GPIO.input(misopin):
        #                 adcout |= 0x1
        #
        # GPIO.output(cspin, True)
        #
        # adcout >>= 1       # first bit is 'null' so drop it
        # return adcout


