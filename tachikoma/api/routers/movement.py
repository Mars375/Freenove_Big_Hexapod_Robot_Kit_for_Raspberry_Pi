from fastapi import APIRouter, HTTPException, Query
import asyncio
from tachikoma.api.models import MoveCommand, AttitudeCommand, StandardResponse
from tachikoma.core.robot_controller import get_robot_controller, initialize_robot
from tachikoma.core.exceptions import HardwareNotAvailableError, CommandExecutionError
import structlog


router = APIRouter()
logger = structlog.get_logger()


@router.post("/move", response_model=StandardResponse)
async def move_robot(command: MoveCommand):
    """Execute movement command"""
    logger.info("movement.move", mode=command.mode, x=command.x, y=command.y,
                speed=command.speed, angle=command.angle)

    try:
        robot = await initialize_robot()
        await robot.movement.move(
            mode=command.mode,
            x=command.x,
            y=command.y,
            speed=command.speed,
            angle=command.angle
        )

        return StandardResponse(
            success=True,
            message="Movement command sent successfully",
            command=f"CMD_MOVE#{command.mode}#{command.x}#{command.y}#{command.speed}#{command.angle}"
        )

    except HardwareNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except CommandExecutionError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/attitude", response_model=StandardResponse)
async def set_attitude(command: AttitudeCommand):
    """Set robot attitude (roll, pitch, yaw)"""
    logger.info("movement.attitude", roll=command.roll, pitch=command.pitch, yaw=command.yaw)

    try:
        robot = await initialize_robot()
        await robot.movement.set_attitude(
            roll=command.roll,
            pitch=command.pitch,
            yaw=command.yaw
        )

        return StandardResponse(
            success=True,
            message="Attitude set successfully",
            data={
                "roll": command.roll,
                "pitch": command.pitch,
                "yaw": command.yaw
            }
        )

    except HardwareNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except CommandExecutionError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop", response_model=StandardResponse)
async def stop_robot():
    """Emergency stop"""
    logger.info("movement.stop")

    try:
        robot = await initialize_robot()
        await robot.movement.stop()

        return StandardResponse(
            success=True,
            message="Robot stopped successfully"
        )

    except HardwareNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except CommandExecutionError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test_walk")
async def test_walk(
    speed: int = 5,
    duration: float = 5.0
):
    """Test walk forward for debugging."""
    try:
        logger.info("movement.test_walk.initiated")
        
        robot = await initialize_robot()
        
        logger.info("movement.test_walk.starting_forward_movement")
        await robot.movement.move(
            gait_type="1",
            mode="forward",
            x=0,
            y=25,
            speed=speed,
            angle=0
        )
        
        logger.info("movement.test_walk.walking", duration=duration)
        await asyncio.sleep(duration)
        
        logger.info("movement.test_walk.stopping")
        await robot.movement.stop()
        
        logger.info("movement.test_walk.completed")
        return {"status": "success", "message": f"Walk test completed with speed {speed}"}
    except Exception as e:
        logger.error("movement.test_walk.failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/calibrate/{leg_id}/{joint}")
async def calibrate_servo(
    leg_id: int,  # 0-5 (pattes)
    joint: str,   # "coxa", "femur", "tibia"
    angle: int = Query(..., ge=0, le=180)
):
    """
    Calibrate individual servo position.
    leg_id: 0=front-right, 1=middle-right, 2=back-right, 
            3=back-left, 4=middle-left, 5=front-left
    joint: coxa/femur/tibia
    angle: 0-180 degrees
    """
    robot = await initialize_robot()
    
    # Map joint name to servo index (0-2 per leg)
    joint_map = {"coxa": 0, "femur": 1, "tibia": 2}
    joint_idx = joint_map[joint]
    
    # Calculate absolute servo channel (0-17)
    servo_channel = (leg_id * 3) + joint_idx
    
    # Move servo to angle
    robot.movement.servo_controller.set_servo_angle(servo_channel, angle)
    
    return {
        "leg": leg_id,
        "joint": joint,
        "angle": angle,
        "servo_channel": servo_channel
    }

@router.post("/calibrate/save")
async def save_calibration(calibration_data: dict):
    """
    Save calibration angles to point.txt
    Format: {"leg_id": {"coxa": angle, "femur": angle, "tibia": angle}, ...}
    """
    with open("point.txt", "w") as f:
        for leg_id in range(6):
            leg_data = calibration_data.get(str(leg_id), {})
            coxa = leg_data.get("coxa", 90)
            femur = leg_data.get("femur", 90)
            tibia = leg_data.get("tibia", 90)
            f.write(f"{coxa},{femur},{tibia}\n")
    
    return {"status": "saved", "file": "point.txt"}
