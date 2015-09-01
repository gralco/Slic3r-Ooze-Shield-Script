#!/usr/bin/python
import sys

def find_gcode_line(lines, code, layer_height = None, retract_lift = None, reverse = False):
  for line in reversed(lines) if reverse else lines:
    if(code in line):
      if(layer_height == retract_lift and lines[lines.index(line)] == lines[lines.index(line)+2]):
        continue
      else:
        return lines.index(line)
  return -1

#Open
gcode = open(sys.argv[1], 'r+')
lines = gcode.readlines()
found_toolchange = False
found_first_G92_E0 = False

shield_line_range = []

for line in list(enumerate(lines)):
  if not found_toolchange and "; Tool change from 1 to 0" in line[1]:
    shield_line_range.append([line[0]])
    found_toolchange = True
  elif not found_first_G92_E0 and found_toolchange and "G92 E0" in line[1]:
    found_toolchange = False
    found_first_G92_E0 = True
  elif found_first_G92_E0 and "G92 E0" in line[1]:
    shield_line_range[-1].append(line[0]+2)
    found_first_G92_E0 = False

file = open("Shield.gcode", 'w+')

print shield_line_range

secondary_extruder_shield_code = []
for i in range(len(shield_line_range)):
  secondary_extruder_shield_code.append([])
  for line in lines[shield_line_range[i][0]:shield_line_range[i][1]]:
    if 'T0' in line:
      secondary_extruder_shield_code[i].append('T1\n')
    elif 'Z' in line:
      height = float(line[4:].split(' F')[0]) - 0.18
      newline = line[0:line.index('Z')+1] + str(height) + line[line.index(' F'):]
      secondary_extruder_shield_code[i].append(newline)
    elif 'E' in line and 'F' in line and not 'Y' in line and not 'X' in line and not 'Z' in line:
      length = float(line[line.index('E')+1:line.index(' F')])
      flow_rate = float(line[line.index(' F')+2:])
      newline = line[:line.index('E')+1] + str(3*length/4) + ' F' + str(3*flow_rate/4) + '\n'
      secondary_extruder_shield_code[i].append(newline)
    else:
      secondary_extruder_shield_code[i].append(line)

secondary_extruder_shield_code.append([])

c=0
i=0
for line in list(enumerate(lines)):
  if "; Tool change from 0 to 1" in line[1]:
    lines = lines[:i+1] + secondary_extruder_shield_code[c] + lines[i+1:]
    i+=len(secondary_extruder_shield_code[c])
    c+=1
  i+=1

copy_current_chunk = True
for i in range(len(shield_line_range)):
  for line in lines[shield_line_range[i][0]:shield_line_range[i][1]]:
    if 'E' in line and 'F' in line and not 'Y' in line and not 'X' in line and not 'Z' in line:
      length = float(line[line.index('E')+1:line.index(' F')])
      flow_rate = float(line[line.index(' F')+2:])
      newline = line[:line.index('E')+1] + str(3*length/4) + ' F' + str(3*flow_rate/4) + '\n'
      file.write(newline)
    else:
      file.write(line)
  for line in secondary_extruder_shield_code[i]:
    file.write(line)

#Save
lines = ''.join(lines)
gcode.seek(0)
gcode.write(lines)
gcode.close()


"""
#Logic
first_layer_height_percent = float(lines[find_gcode_line(lines, "; first_layer_height = ", True)].split(' ')[3].replace('%', '').strip())/100.0
#print "First Layer Height Percent: " + str(first_layer_height_percent)
layer_height = float(lines[find_gcode_line(lines, "; layer_height = ", True)].split(' ')[3].strip())
#print "Layer Height: " + str(layer_height)
#retract_lift = float(lines[find_gcode_line(lines, "; retract_lift = ", True)].split(' ')[3].strip())
#print "Retract Lift: " + str(retract_lift)
#z_height = z_offset+first_layer_height_percent*layer_height+layer_height*(int(layer_number)-1)


#Edit
line_number = 0
lines.insert(line_number, "; WORK HERE\n")


#Save
lines = ''.join(lines)
gcode.seek(0)
gcode.write(lines)
gcode.close()
"""
