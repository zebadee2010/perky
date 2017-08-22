import Adafruit_CharLCD as LCD
lcd = LCD.Adafruit_CharLCDPlate()

buttons = ( (LCD.SELECT, 'Select', (1,1,1)),
            (LCD.LEFT,   'Left'  , (1,0,0)),
            (LCD.UP,     'Up'    , (0,0,1)),
            (LCD.DOWN,   'Down'  , (0,1,0)),
            (LCD.RIGHT,  'Right' , (1,0,1)) )

while True:
     for button in buttons:
             if lcd.is_pressed(button[0]):
                     lcd.clear()
                     lcd.message(button[1])
                     lcd.set_color(button[2][0], button[2][1], button[2][2])

