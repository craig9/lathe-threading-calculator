#!/usr/bin/python

from operator import mul,itemgetter
import sys
from itertools import permutations
from math import pi, cos

gears = [20, 30, 32, 35, 45, 50, 50, 55, 60, 64, 64, 64, 65]

quad_gears = {1:1, 63:80, 70:80, 80:63, 80:70}

qc_gears = {1:16, 2:18, 3:19, 4:20, 5:22, 6:24, 7:26, 8:28, 9:30, 10:32}

#iso_mm_pitches = [.20, .25, .30, .35, .40, .45, .50, .60, .70, .75, .80, 1.00, 1.25, 1.50, 1.75, 2.00, 2.50, 3.00, 3.50, 4.00, 4.50, 5.00, 5.50, 6.00, 7.854]

iso_mm_pitches = [3.996, 4.987, 4.995, 7.854] # <-- Totally custom pitches

#desired_tpis = [2, 2.5, 3, 3.5, 4, 4.5, 4.75, 5, 5.5, 6, 6.5, 7, 8, 9, 9.5, 10, 11, 12, 13, 14, 16, 18, 19, 20, 22, 24, 26, 27, 28, 32, 36, 38, 40, 44, 48, 52, 56, 64, 72, 76, 80, 88, 96, 104, 112, 128, 144, 152, 160, 176, 192, 208, 224]

desired_tpis = [48/pi, 32/pi, 24/pi, 20/pi, 18/pi, 5.1211, 16/pi, 12/pi]

#new_gear_options = [16, 18, 20, 22, 24, 25, 26, 27, 28, 30, 32, 33, 36, 39, 40, 42, 44, 45, 46, 48, 50, 52, 54, 56, 57, 60, 61, 72, 80, 100]

leadscrew_tpi = 8.0

def try_combination(stud_gear, leadscrew_gear, quadrant_1, quadrant_2, qc_gear, leadscrew_tpi):
    change_gear_ratio = float(stud_gear) / float(leadscrew_gear)
    quadrant_ratio = float(quadrant_1) / float(quadrant_2)
    qc_ratio = float(16.0) / float(qc_gear)
    tpi = leadscrew_tpi / (change_gear_ratio * quadrant_ratio * qc_ratio)
    mm_pitch = 25.4 / tpi
    return (tpi, mm_pitch)

def calc_error(desired, actual):
    diff = actual - desired
    percent_error = diff / desired * 100.0
    return percent_error

def find_best_combo(gears, quad_gears, qc_gears, desired_mm_pitch):
    results = []

    for items in permutations(gears, 2):
        for qc_key in qc_gears:
            for quad_driver in quad_gears:
                qc_gear = qc_gears[qc_key]
                quad_driven = quad_gears[quad_driver]

                (tpi, mm_pitch) = try_combination(items[0], quad_driver, quad_driven, items[1], qc_gear, leadscrew_tpi)

                percent_error = calc_error(desired_mm_pitch, mm_pitch)
                info_string = "%.2f, %s, %s, %s, %s, Gearbox %s (16/%s), %.4f, %+.3f%%" % \
                              (desired_mm_pitch, items[0], quad_driver, quad_driven, items[1],  qc_key, 
                                qc_gears[qc_key], mm_pitch, percent_error)
                results.append((percent_error, info_string))

    sorted_results = sorted(results, key=lambda item: abs(item[0]))

    

#    print "Top ten:"
#    for i in range(len(sorted_results)):
#        if abs(sorted_results[i][0]) < 1:
#            print sorted_results[i]
    return sorted_results[0] # (error, info_string)

def find_best_tpi_combo(gears, quad_gears, qc_gears, desired_tpi):
    results = []

    for items in permutations(gears, 4):
        for ikey in qc_gears:
            i = qc_gears[ikey]
            (tpi, mm_pitch) = try_combination(items[0], items[1], items[2], items[3], i, leadscrew_tpi)
            percent_error = calc_error(desired_tpi, tpi)
            info_string = "%.2f, %s, %s, %s, %s, %s (16/%s), %.4f, %+.3f%%" % \
                          (desired_tpi, items[0], items[1], items[2], items[3], ikey, qc_gears[ikey], tpi, percent_error)
            results.append((percent_error, info_string))
    sorted_results = sorted(results, key=lambda item: abs(item[0]))
    return sorted_results[0] # (error, info_string)

def print_errors(errors):
    average_error = 0
    for e in errors:
        average_error += abs(e)
    average_error = average_error / len(errors)
    print "Average error: %.3f%%" % average_error,
    try:
        print "(1 in %d)" % (100/average_error)
    except:
        print
    return average_error

def print_best_combos(gears, quad_gears, qc_gears, desired_mm_pitches):
    errors = []

    for desired_mm_pitch in desired_mm_pitches:
        (error, info_string) = find_best_combo(gears, quad_gears, qc_gears, desired_mm_pitch)
        errors.append(error)
        print info_string

    print
    average_error = print_errors(errors)
    return average_error

def print_best_tpi_combos(gears, quad_gears, qc_gears, desired_tpis):
    errors = []

    for desired_tpi in desired_tpis:
        (error, info_string) = find_best_tpi_combo(gears, quad_gears, qc_gears, desired_tpi)
        errors.append(error)
        print info_string

    print
    average_error = print_errors(errors)
    return average_error

def metric_main(suggest_new):
    gear_errors = {}

    print_best_combos(gears, quad_gears, qc_gears, iso_mm_pitches)
    print

    if not suggest_new:
        return

    for new_gear in new_gear_options:
        print "Using this set of gears: ", ", ".join([str(g) for g in gears])
        print "Temporarily adding gear: %d" % new_gear
        gears.append(new_gear)
        gear_errors[new_gear] = print_best_combos(gears, quad_gears, qc_gears, iso_mm_pitches)
        gears.pop()
        print

    sorted_gear_errors = sorted(gear_errors.items(), key=itemgetter(1))

    for (key, val) in sorted_gear_errors[:10]:
        print key, "%.3f%%" % val

def imperial_main(suggest_new):
    gear_errors = {}
    
    print_best_tpi_combos(gears, qc_gears, desired_tpis)
    print

    if not suggest_new:
        return

    for new_gear in new_gear_options:
        print "Using this set of gears: ", ", ".join([str(g) for g in gears])
        print "Temporarily adding gear: %d" % new_gear
        gears.append(new_gear)
        gear_errors[new_gear] = print_best_tpi_combos(gears, quad_gears, qc_gears, desired_tpis)
        gears.pop()
        print

    sorted_gear_errors = sorted(gear_errors.items(), key=itemgetter(1))

    for (key, val) in sorted_gear_errors[:10]:
        print key, "%.3f%%" % val

def main():
    print "Using this set of gears: ", ", ".join([str(g) for g in gears])
    print
    metric_main(suggest_new=False)
    #imperial_main(suggest_new=False)
    print "QC Tumbler:"
    for k in sorted(qc_gears):
        print "%s: %s/%s" % (k, 16, qc_gears[k])

main()
