# Written by K. M. Knausgård 2023-10-29
import cadquery as cq
from cadquery.vis import show


def create_handle(length, gap_width, wall_thickness, width):
    tool_base = (cq.Workplane("XY")
                 .box(length - gap_width, gap_width + 2 * wall_thickness, width, centered=(False, True, False))
                 .union(
        cq.Workplane("XY").moveTo(x=length - gap_width, y=0).circle(0.5 * (gap_width + 2 * wall_thickness)).extrude(
            width)))

    tool_remove = (cq.Workplane("XY").moveTo(x=0, y=0)
                   .box(length - gap_width, gap_width, width, centered=(False, True, False))
                   .union(cq.Workplane("XY").moveTo(x=length - gap_width, y=0).circle(0.5 * gap_width).extrude(width)))

    return tool_base.cut(tool_remove)


def create_finger_presspoint(length, gap_width, wall_thickness, width):
    sPnts = [(0, 0), (0, 0.3), (-3, 0.7 * gap_width / 2), (-7, 0.9 * gap_width / 2), (-9, 1.0 * gap_width / 2),
             (-9, 1.0 * gap_width / 2 + 0.5 * wall_thickness), (-9 + 1.5, 1.0 * gap_width / 2 + 0.5 * wall_thickness),
             (-9 + 1.5, 1.0 * gap_width / 2), (-7 + 1.3, 0.9 * gap_width / 2), (-3 + 1.1, 0.7 * gap_width / 2),
             (0 + 1.0, 0.3), (0 + 1.0, 0)]
    finger_presspoint = (cq.Workplane("XY").center(x=(1 / 2) * length, y=0)
                         .spline(sPnts).close().extrude(width)
                         .union(
        cq.Workplane("XY").center(x=(1 / 2) * length, y=0).spline(sPnts).close().extrude(width).mirror((0, 1, 0))))
    return finger_presspoint


def create_gripper(grip_x_pos, gap_width, gripper_length, grip_depth, width):
    gripper = (cq.Workplane("XY").center(x=grip_x_pos, y=-0.5 * gap_width)
               .line(xDist=gripper_length + .5, yDist=grip_depth).line(xDist=-0.5, yDist=-grip_depth).close().extrude(
        width)
               .union(cq.Workplane("XY").center(x=grip_x_pos, y=-0.5 * gap_width).line(xDist=gripper_length + .5,
                                                                                       yDist=grip_depth).line(
        xDist=-0.5, yDist=-grip_depth).close().extrude(width).mirror((0, 1, 0))))
    return gripper


def create_stiffness_segment(length, gap_width, width):
    stiffness_segment = (cq.Workplane("XY").center(x=(1 / 2) * length - 5, y=-gap_width / 2)
                         .threePointArc(((1 / 6) * length, 3), ((2 / 6) * length, 0)).close().extrude(width)
                         .union(cq.Workplane("XY").center(x=(1 / 2) * length - 5, y=-gap_width / 2)
                                .threePointArc(((1 / 6) * length, 3), ((2 / 6) * length, 0)).close().extrude(
        width).mirror((0, 1, 0))))
    return stiffness_segment


def emboss_text(tool, length, gap_width, width, emboss_depth):
    tool = tool.faces(">Y").workplane(origin=((length - gap_width) / 2, 0, width / 2)) \
        .text("NutX for TESLA MODEL S", fontsize=0.65 * width, distance=-emboss_depth, combine='cut')
    tool = tool.faces("<Y").workplane(origin=((length - gap_width) / 2, 0, width / 2 + 1)) \
        .text("By x.com/knausgard", fontsize=0.65 * width, distance=-emboss_depth, combine='cut')
    return tool


def generate_tesla_model_s_wheel_lug_nut_caps_removal_tool():
    print("Starting up..")

    # Configuration
    config = {
        "file_name": "tesla_lug_nut_cap_removal_tool.3mf",
        "length": 120,
        "gap_width": 25,
        "wall_thickness": 2,
        "width": 11,
        "emboss_depth": 0.3,
        "grip_depth": 1.5,
        "gripper_length": 7,
        "grip_x_pos": 5
    }

    tool = create_handle(config['length'], config['gap_width'], config['wall_thickness'], config['width'])
    tool = tool.edges("|Z and <X and (>>Y[2] or <<Y[2])").chamfer(1.3)  # Must happen before fillet.
    tool = tool.edges("|Z and <X and (>Y or <Y)").fillet(0.4)
    tool = tool.edges("<X or >X").fillet(0.4)


    tool = tool.union(
        create_finger_presspoint(config['length'], config['gap_width'], config['wall_thickness'], config['width']))
    tool = tool.union(
        create_gripper(config['grip_x_pos'], config['gap_width'], config['gripper_length'], config['grip_depth'],
                       config['width']))
    tool = tool.union(create_stiffness_segment(config['length'], config['gap_width'], config['width']))
    tool = emboss_text(tool, config['length'], config['gap_width'], config['width'], config['emboss_depth'])

    print("Showing results, close to continue with export..")
    show(tool)
    print("Exporting..")
    cq.exporters.export(tool, config['file_name'], "3MF", tolerance=0.05, angularTolerance=0.05)
    print("Completed..")

    # macOS open Cura
    # subprocess.run(["open", config['file_name']])
    # subprocess.run(["open", "-a", "UltiMaker Cura", config['file_name']])


if __name__ == '__main__':
    generate_tesla_model_s_wheel_lug_nut_caps_removal_tool()
