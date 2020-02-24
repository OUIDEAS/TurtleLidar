from Raspi_MotorHAT import Raspi_MotorHAT

mh = Raspi_MotorHAT(0x6F)

def turnOffMotors():
    mh.getMotor(1).run(Raspi_MotorHAT.RELEASE)
    mh.getMotor(2).run(Raspi_MotorHAT.RELEASE)
    mh.getMotor(3).run(Raspi_MotorHAT.RELEASE)
    mh.getMotor(4).run(Raspi_MotorHAT.RELEASE)


def run():
    # Stepper Motors
    PanStepper = mh.getStepper(200, 2)
    PanStepper.setSpeed(10)
    TiltStepper = mh.getStepper(200, 1)
    TiltStepper.setSpeed(10)

    try:
        while True:
            pan = int(input("Pan how many steps: "))
            if pan > 0:
                PanStepper.step(pan, Raspi_MotorHAT.FORWARD, Raspi_MotorHAT.MICROSTEP)
            else:
                PanStepper.step(abs(pan), Raspi_MotorHAT.BACKWARD, Raspi_MotorHAT.MICROSTEP)

            tilt = int(input("Tilt how many steps: "))
            if tilt > 0:
                TiltStepper.step(tilt, Raspi_MotorHAT.FORWARD, Raspi_MotorHAT.MICROSTEP)
            else:
                TiltStepper.step(abs(tilt), Raspi_MotorHAT.BACKWARD, Raspi_MotorHAT.MICROSTEP)
            stop = int(input("Type 7 to stop: "))
            if stop == 7:
                break

    except Exception as e:
        print("Stopping due to error:", e)
        turnOffMotors()


if __name__ == '__main__':
    run()
    turnOffMotors()
